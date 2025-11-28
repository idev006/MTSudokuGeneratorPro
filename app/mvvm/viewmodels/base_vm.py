from PySide6.QtCore import QObject, Signal

class BaseViewModel(QObject):
    """
    Base class for all ViewModels.
    Implements the INotifyPropertyChanged pattern using Qt Signals.
    """
    # Generic signal for property changes: (property_name, new_value)
    property_changed = Signal(str, object)

    def __init__(self):
        super().__init__()

    def notify_property_changed(self, property_name: str, value: object):
        """Emits the property_changed signal."""
        self.property_changed.emit(property_name, value)
