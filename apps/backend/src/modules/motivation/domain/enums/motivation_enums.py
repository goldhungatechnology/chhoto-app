from enum import Enum


class QuotesStatusEnum(str, Enum):
    """
    Enum for valid quote statuses.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    # DRAFT = "draft" # it's handle by FE as per current requirements


class QuotesTextStyleEnum(str, Enum):
    """
    Enum for valid quote text styles.
    """

    TIMES_NEW_ROMAN = "times_new_roman"
    ARIAL = "arial"
    PLAYFAIR_DISPLAY = "playfair_display"
    MERRIWEATHER = "merriweather"
    GEORGIA = "georgia"
    GARAMOND = "garamond"
    BASKERVILLE = "baskerville"
