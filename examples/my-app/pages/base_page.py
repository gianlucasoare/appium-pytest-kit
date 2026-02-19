"""Base page all page objects inherit from."""


from appium_pytest_kit import MobileActions, Waiter


class BasePage:
    """Holds driver, waiter and actions — injected from framework fixtures."""

    def __init__(self, driver, waiter: Waiter, actions: MobileActions) -> None:
        self.driver = driver
        self.waiter = waiter
        self.actions = actions
