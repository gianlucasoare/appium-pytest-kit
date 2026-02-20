"""Base class for all flows."""


from appium_pytest_kit import MobileActions, Waiter


class BaseFlow:
    """Thin composition base providing driver, waiter and actions.

    Flows orchestrate multi-page journeys. Unlike page objects (which model
    a single screen), a flow coordinates several pages to complete a user
    journey — e.g. "log in, open settings, change language, log out".
    """

    def __init__(self, driver, waiter: Waiter, actions: MobileActions) -> None:
        self.driver = driver
        self.waiter = waiter
        self.actions = actions
