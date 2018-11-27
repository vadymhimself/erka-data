import os

from pyspark import StorageLevel
from pyspark.ml.recommendation import ALSModel
from pyspark.ml.fpm import FPGrowthModel
from pyspark.sql.functions import *

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    A product recommendation engine
    """

    def get_association_rules(self, product_id):
        """
        Searches for association rules
        """
        return self._fpm_model.associationRules\
            .filter(array_contains('antecedent', product_id)) \
            .sort(desc('confidence'))\
            .toJSON()\
            .collect()

    def get_items_for_user(self, phone):
        """
        Searches for item recommendations
        """
        numeric_tel = ''.join(filter(str.isdigit, phone))
        hashed_tel = int(numeric_tel) * 67853 % 2**31
        return self._item_recommendations.filter(col('telHashed') == hashed_tel)\
            .select(explode('recommendations'))\
            .select('col.goodsId', 'col.rating')\
            .toJSON()\
            .collect()

    def __init__(self, sc, model_dir):
        """
        Init the recommendation engine given a Spark context and models path
        """

        logger.info("Starting up the Recommendation Engine: ")

        self.sc = sc

        # Load models
        logger.info("Loading models...")
        als_path = os.path.join(model_dir, 'als_model')
        self._als_model = ALSModel.load(als_path)
        fpm_path = os.path.join(model_dir, 'fpm_model')
        self._fpm_model = FPGrowthModel.load(fpm_path)

        logger.info("Caching precomputed recommendations...")
        self._item_recommendations = self._als_model.recommendForAllUsers(3)\
            .persist(StorageLevel.MEMORY_AND_DISK)
