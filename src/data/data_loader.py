"""
Data loader for Smart Bottle ML Service
Loads data from CSV files and MySQL database
"""
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Tuple
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from config.database import get_connection

logger = logging.getLogger(__name__)


class SmartBottleDataLoader:
    """Data loader for Smart Bottle system"""

    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialize data loader

        Args:
            data_dir: Directory containing CSV data files
        """
        self.data_dir = Path(data_dir)
        self.formula_df = None
        self.feeding_logs_df = None

    def load_csv_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Load legacy CSV data files

        Returns:
            Tuple of (formula_df, feeding_logs_df)
        """
        try:
            # Load formula master data
            formula_path = self.data_dir / "formula_master.csv"
            self.formula_df = pd.read_csv(formula_path)
            logger.info(f"Loaded {len(self.formula_df)} formulas from CSV")

            # Load feeding logs
            feeding_path = self.data_dir / "feeding_logs.csv"
            self.feeding_logs_df = pd.read_csv(feeding_path)
            logger.info(f"Loaded {len(self.feeding_logs_df)} feeding logs from CSV")

            return self.formula_df, self.feeding_logs_df

        except FileNotFoundError as e:
            logger.error(f"CSV file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise

    def load_formulas_from_db(self) -> pd.DataFrame:
        """
        Load formula data from database
        Note: This assumes a 'formulas' table exists in Smart Bottle DB
        If not, returns CSV data

        Returns:
            DataFrame with formula information
        """
        try:
            conn = get_connection()
            query = """
            SELECT
                formula_id,
                formula_brand,
                category,
                lactose_level,
                target_issue,
                protein_type
            FROM formulas
            """
            df = pd.read_sql(query, conn)
            conn.close()

            logger.info(f"Loaded {len(df)} formulas from database")
            return df

        except Exception as e:
            logger.warning(f"Could not load from database: {e}")
            logger.info("Falling back to CSV data")
            if self.formula_df is None:
                self.load_csv_data()
            return self.formula_df

    def load_feeding_records(
        self,
        baby_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Load feeding records from Smart Bottle database

        Args:
            baby_id: Filter by specific baby (optional)
            limit: Maximum number of records (optional)

        Returns:
            DataFrame with feeding records
        """
        try:
            conn = get_connection()

            query = """
            SELECT
                fr.feeding_id,
                fr.baby_id,
                fr.formula_id,
                fr.amount_consumed,
                fr.temperature,
                fr.duration,
                fr.timestamp,
                b.birth_date,
                TIMESTAMPDIFF(MONTH, b.birth_date, fr.timestamp) as age_month
            FROM feeding_records fr
            JOIN babies b ON fr.baby_id = b.baby_id
            WHERE 1=1
            """

            params = []

            if baby_id is not None:
                query += " AND fr.baby_id = %s"
                params.append(baby_id)

            query += " ORDER BY fr.timestamp DESC"

            if limit is not None:
                query += " LIMIT %s"
                params.append(limit)

            df = pd.read_sql(query, conn, params=params if params else None)
            conn.close()

            logger.info(f"Loaded {len(df)} feeding records from database")
            return df

        except Exception as e:
            logger.error(f"Error loading feeding records: {e}")
            raise

    def load_baby_profile(self, baby_id: int) -> dict:
        """
        Load baby profile information

        Args:
            baby_id: Baby identifier

        Returns:
            Dictionary with baby profile
        """
        try:
            conn = get_connection()

            query = """
            SELECT
                b.baby_id,
                b.name,
                b.birth_date,
                b.gender as sex,
                TIMESTAMPDIFF(MONTH, b.birth_date, NOW()) as age_month,
                b.weight_at_birth
            FROM babies b
            WHERE b.baby_id = %s
            """

            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (baby_id,))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result is None:
                raise ValueError(f"Baby with ID {baby_id} not found")

            logger.info(f"Loaded profile for baby {baby_id}")
            return result

        except Exception as e:
            logger.error(f"Error loading baby profile: {e}")
            raise

    def load_recent_feeding_stats(
        self,
        baby_id: int,
        days: int = 30
    ) -> dict:
        """
        Load recent feeding statistics for a baby

        Args:
            baby_id: Baby identifier
            days: Number of days to look back

        Returns:
            Dictionary with feeding statistics
        """
        try:
            conn = get_connection()

            query = """
            SELECT
                COUNT(*) as total_feedings,
                AVG(amount_consumed) as avg_amount_ml,
                STD(amount_consumed) as std_amount_ml,
                SUM(amount_consumed) as total_amount_ml,
                AVG(temperature) as avg_temperature,
                AVG(duration) as avg_duration_min,
                MIN(timestamp) as first_feeding,
                MAX(timestamp) as last_feeding
            FROM feeding_records
            WHERE baby_id = %s
              AND timestamp >= DATE_SUB(NOW(), INTERVAL %s DAY)
            """

            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (baby_id, days))
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result and result['total_feedings'] > 0:
                # Calculate feeding frequency
                result['feeding_frequency'] = result['total_feedings'] / days

                logger.info(f"Loaded {days}-day stats for baby {baby_id}")
                return result
            else:
                logger.warning(f"No feeding data found for baby {baby_id}")
                return {}

        except Exception as e:
            logger.error(f"Error loading feeding stats: {e}")
            raise

    def prepare_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare merged data for model training

        Returns:
            Tuple of (X, y) - features and target
        """
        try:
            # Load data
            formula_df, feeding_logs_df = self.load_csv_data()

            # Merge formula info with feeding logs
            data = feeding_logs_df.merge(formula_df, on="formula_id", how="left")

            # Define features
            baby_features = [
                "age_month",
                "sex",
                "height_cm",
                "weight_kg",
                "allergy_risk",
                "lactose_sensitivity",
                "feed_ml_per_intake",
            ]

            formula_features = [
                "formula_id",
                "category",
                "lactose_level",
                "target_issue",
                "protein_type",
            ]

            feature_cols = baby_features + formula_features
            target_col = "overall_tolerance"

            X = data[feature_cols].copy()
            y = data[target_col].copy()

            logger.info(f"Prepared training data: {len(X)} samples, {len(feature_cols)} features")

            return X, y

        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            raise


if __name__ == "__main__":
    # Test data loader
    logging.basicConfig(level=logging.INFO)

    loader = SmartBottleDataLoader()

    print("\n=== Testing CSV Data Loading ===")
    formula_df, feeding_df = loader.load_csv_data()
    print(f"Formulas: {len(formula_df)}")
    print(f"Feeding logs: {len(feeding_df)}")

    print("\n=== Formula Data Sample ===")
    print(formula_df.head())

    print("\n=== Feeding Logs Sample ===")
    print(feeding_df.head())

    print("\n=== Preparing Training Data ===")
    X, y = loader.prepare_training_data()
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
