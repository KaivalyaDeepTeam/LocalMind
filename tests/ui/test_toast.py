"""
Tests for Toast Notification System.

Tests the ToastType enum, ToastNotification widget,
ToastManager, and related functionality.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestToastTypeEnum:
    """Tests for ToastType enumeration."""

    def test_toast_type_success_value(self):
        """Test SUCCESS enum value."""
        from localmind.ui.toast import ToastType

        assert ToastType.SUCCESS.value == "success"

    def test_toast_type_error_value(self):
        """Test ERROR enum value."""
        from localmind.ui.toast import ToastType

        assert ToastType.ERROR.value == "error"

    def test_toast_type_warning_value(self):
        """Test WARNING enum value."""
        from localmind.ui.toast import ToastType

        assert ToastType.WARNING.value == "warning"

    def test_toast_type_info_value(self):
        """Test INFO enum value."""
        from localmind.ui.toast import ToastType

        assert ToastType.INFO.value == "info"

    def test_toast_type_count(self):
        """Test there are exactly 4 toast types."""
        from localmind.ui.toast import ToastType

        assert len(ToastType) == 4

    def test_toast_type_iteration(self):
        """Test all toast types can be iterated."""
        from localmind.ui.toast import ToastType

        types = list(ToastType)
        assert ToastType.SUCCESS in types
        assert ToastType.ERROR in types
        assert ToastType.WARNING in types
        assert ToastType.INFO in types


class TestDefaultDurations:
    """Tests for DEFAULT_DURATIONS dictionary."""

    def test_success_duration(self):
        """Test SUCCESS toast duration is 4000ms."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastType

        assert DEFAULT_DURATIONS[ToastType.SUCCESS] == 4000

    def test_info_duration(self):
        """Test INFO toast duration is 5000ms."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastType

        assert DEFAULT_DURATIONS[ToastType.INFO] == 5000

    def test_warning_duration(self):
        """Test WARNING toast duration is 6000ms."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastType

        assert DEFAULT_DURATIONS[ToastType.WARNING] == 6000

    def test_error_duration(self):
        """Test ERROR toast duration is 8000ms."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastType

        assert DEFAULT_DURATIONS[ToastType.ERROR] == 8000

    def test_error_has_longest_duration(self):
        """Test ERROR has longest duration for user to read."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastType

        error_duration = DEFAULT_DURATIONS[ToastType.ERROR]
        for toast_type, duration in DEFAULT_DURATIONS.items():
            if toast_type != ToastType.ERROR:
                assert error_duration > duration

    def test_success_has_shortest_duration(self):
        """Test SUCCESS has shortest duration."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastType

        success_duration = DEFAULT_DURATIONS[ToastType.SUCCESS]
        for toast_type, duration in DEFAULT_DURATIONS.items():
            if toast_type != ToastType.SUCCESS:
                assert success_duration < duration

    def test_all_durations_positive(self):
        """Test all durations are positive integers."""
        from localmind.ui.toast import DEFAULT_DURATIONS

        for duration in DEFAULT_DURATIONS.values():
            assert isinstance(duration, int)
            assert duration > 0


class TestToastNotificationStyles:
    """Tests for ToastNotification STYLES dictionary."""

    def test_success_style_exists(self, qapp):
        """Test SUCCESS style is defined."""
        from localmind.ui.toast import ToastNotification, ToastType

        assert ToastType.SUCCESS in ToastNotification.STYLES

    def test_error_style_exists(self, qapp):
        """Test ERROR style is defined."""
        from localmind.ui.toast import ToastNotification, ToastType

        assert ToastType.ERROR in ToastNotification.STYLES

    def test_warning_style_exists(self, qapp):
        """Test WARNING style is defined."""
        from localmind.ui.toast import ToastNotification, ToastType

        assert ToastType.WARNING in ToastNotification.STYLES

    def test_info_style_exists(self, qapp):
        """Test INFO style is defined."""
        from localmind.ui.toast import ToastNotification, ToastType

        assert ToastType.INFO in ToastNotification.STYLES

    def test_success_style_has_required_keys(self, qapp):
        """Test SUCCESS style has all required keys."""
        from localmind.ui.toast import ToastNotification, ToastType

        style = ToastNotification.STYLES[ToastType.SUCCESS]
        required_keys = ["bg", "border", "text", "icon", "bg_dark", "text_dark"]
        for key in required_keys:
            assert key in style

    def test_success_icon_is_checkmark(self, qapp):
        """Test SUCCESS icon is checkmark."""
        from localmind.ui.toast import ToastNotification, ToastType

        style = ToastNotification.STYLES[ToastType.SUCCESS]
        assert style["icon"] == "✓"

    def test_error_icon_is_x(self, qapp):
        """Test ERROR icon is X."""
        from localmind.ui.toast import ToastNotification, ToastType

        style = ToastNotification.STYLES[ToastType.ERROR]
        assert style["icon"] == "✕"

    def test_warning_icon_is_triangle(self, qapp):
        """Test WARNING icon is warning triangle."""
        from localmind.ui.toast import ToastNotification, ToastType

        style = ToastNotification.STYLES[ToastType.WARNING]
        assert style["icon"] == "⚠"

    def test_info_icon_is_i(self, qapp):
        """Test INFO icon is info symbol."""
        from localmind.ui.toast import ToastNotification, ToastType

        style = ToastNotification.STYLES[ToastType.INFO]
        assert style["icon"] == "ℹ"

    def test_all_colors_are_hex(self, qapp):
        """Test all color values are hex format."""
        from localmind.ui.toast import ToastNotification

        for toast_type, style in ToastNotification.STYLES.items():
            for key in ["bg", "border", "text", "bg_dark", "text_dark"]:
                color = style[key]
                assert color.startswith("#"), f"{toast_type}.{key} should be hex color"


class TestToastNotificationWidget:
    """Tests for ToastNotification widget."""

    def test_toast_notification_creates(self, qapp):
        """Test ToastNotification can be created."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO)
        assert toast is not None

    def test_toast_notification_stores_message(self, qapp):
        """Test ToastNotification stores message."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO)
        assert toast._message == "Test message"

    def test_toast_notification_stores_type(self, qapp):
        """Test ToastNotification stores toast type."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.ERROR)
        assert toast._toast_type == ToastType.ERROR

    def test_toast_notification_stores_duration(self, qapp):
        """Test ToastNotification stores duration."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=3000)
        assert toast._duration == 3000

    def test_toast_notification_object_name(self, qapp):
        """Test ToastNotification has correct object name."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO)
        assert toast.objectName() == "toast"

    def test_toast_notification_minimum_width(self, qapp):
        """Test ToastNotification has minimum width."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO)
        assert toast.minimumWidth() == 280

    def test_toast_notification_maximum_width_no_parent(self, qapp):
        """Test ToastNotification max width without parent is 450."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, parent=None)
        assert toast.maximumWidth() == 450

    def test_toast_notification_dark_mode_stored(self, qapp):
        """Test ToastNotification stores dark mode flag."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, dark_mode=True)
        assert toast._dark_mode is True

    def test_toast_notification_action_text_stored(self, qapp):
        """Test ToastNotification stores action text."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification(
            "Test message", ToastType.INFO, action_text="Undo", action_callback=lambda: None
        )
        assert toast._action_text == "Undo"

    def test_toast_notification_closed_signal(self, qapp):
        """Test ToastNotification closed signal can be connected."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=0)
        signal_received = []
        toast.closed.connect(lambda: signal_received.append(True))

        # Manually trigger close
        toast.closed.emit()
        assert len(signal_received) == 1


class TestToastNotificationAnimations:
    """Tests for ToastNotification animations."""

    def test_opacity_effect_created(self, qapp):
        """Test opacity effect is created."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=0)
        assert toast._opacity_effect is not None

    def test_fade_in_animation_created(self, qapp):
        """Test fade in animation is created."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=0)
        assert toast._fade_in is not None

    def test_fade_out_animation_created(self, qapp):
        """Test fade out animation is created."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=0)
        assert toast._fade_out is not None

    def test_fade_in_duration_200ms(self, qapp):
        """Test fade in duration is 200ms."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=0)
        assert toast._fade_in.duration() == 200

    def test_fade_out_duration_200ms(self, qapp):
        """Test fade out duration is 200ms."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test message", ToastType.INFO, duration=0)
        assert toast._fade_out.duration() == 200


class TestToastManager:
    """Tests for ToastManager."""

    def test_toast_manager_creates(self, qapp):
        """Test ToastManager can be created."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        assert manager is not None

    def test_toast_manager_initial_toasts_empty(self, qapp):
        """Test ToastManager starts with empty toast list."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        assert len(manager._toasts) == 0

    def test_toast_manager_default_spacing(self, qapp):
        """Test ToastManager default spacing."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        assert manager._spacing == 12

    def test_toast_manager_default_margin(self, qapp):
        """Test ToastManager default margin."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        assert manager._margin == 20

    def test_toast_manager_default_dark_mode_false(self, qapp):
        """Test ToastManager default dark mode is False."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        assert manager._dark_mode is False

    def test_toast_manager_set_dark_mode(self, qapp):
        """Test ToastManager set_dark_mode."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        manager.set_dark_mode(True)
        assert manager._dark_mode is True

    def test_show_toast_returns_notification(self, qapp):
        """Test show_toast returns a ToastNotification."""
        from localmind.ui.toast import ToastManager, ToastNotification

        manager = ToastManager()
        toast = manager.show_toast("Test message", duration=0)

        assert isinstance(toast, ToastNotification)

    def test_show_toast_adds_to_list(self, qapp):
        """Test show_toast adds toast to list."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        manager.show_toast("Test message", duration=0)

        assert len(manager._toasts) == 1

    def test_show_success_convenience(self, qapp):
        """Test show_success convenience method."""
        from localmind.ui.toast import ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_success("Success!", duration=0)

        assert toast._toast_type == ToastType.SUCCESS

    def test_show_error_convenience(self, qapp):
        """Test show_error convenience method."""
        from localmind.ui.toast import ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_error("Error!", duration=0)

        assert toast._toast_type == ToastType.ERROR

    def test_show_warning_convenience(self, qapp):
        """Test show_warning convenience method."""
        from localmind.ui.toast import ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_warning("Warning!", duration=0)

        assert toast._toast_type == ToastType.WARNING

    def test_show_info_convenience(self, qapp):
        """Test show_info convenience method."""
        from localmind.ui.toast import ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_info("Info!", duration=0)

        assert toast._toast_type == ToastType.INFO

    def test_clear_all_clears_toasts(self, qapp):
        """Test clear_all method."""
        from localmind.ui.toast import ToastManager

        manager = ToastManager()
        manager.show_toast("Toast 1", duration=0)
        manager.show_toast("Toast 2", duration=0)

        # Both toasts are in list
        assert len(manager._toasts) == 2

        # clear_all starts hide animations
        manager.clear_all()
        # Toasts will be removed when animation completes


class TestToastManagerDurationDefaults:
    """Tests for ToastManager default duration behavior."""

    def test_default_success_duration_used(self, qapp):
        """Test SUCCESS uses default 4000ms duration."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_toast("Test", ToastType.SUCCESS)

        assert toast._duration == DEFAULT_DURATIONS[ToastType.SUCCESS]

    def test_default_error_duration_used(self, qapp):
        """Test ERROR uses default 8000ms duration."""
        from localmind.ui.toast import DEFAULT_DURATIONS, ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_toast("Test", ToastType.ERROR)

        assert toast._duration == DEFAULT_DURATIONS[ToastType.ERROR]

    def test_custom_duration_overrides_default(self, qapp):
        """Test custom duration overrides default."""
        from localmind.ui.toast import ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_toast("Test", ToastType.SUCCESS, duration=1000)

        assert toast._duration == 1000

    def test_zero_duration_no_auto_dismiss(self, qapp):
        """Test zero duration means no auto-dismiss."""
        from localmind.ui.toast import ToastManager, ToastType

        manager = ToastManager()
        toast = manager.show_toast("Test", ToastType.INFO, duration=0)

        assert toast._duration == 0


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_init_toast_manager_creates_instance(self, qapp):
        """Test init_toast_manager creates a ToastManager."""
        from localmind.ui import toast

        # Reset global state
        toast._toast_manager = None

        result = toast.init_toast_manager(None)

        assert result is not None
        assert isinstance(result, toast.ToastManager)
        assert toast._toast_manager is result

    def test_get_toast_manager_returns_none_before_init(self, qapp):
        """Test get_toast_manager returns None before initialization."""
        from localmind.ui import toast

        # Reset global state
        toast._toast_manager = None

        result = toast.get_toast_manager()
        assert result is None

    def test_get_toast_manager_returns_instance_after_init(self, qapp):
        """Test get_toast_manager returns instance after initialization."""
        from localmind.ui import toast

        # Reset and initialize
        toast._toast_manager = None
        toast.init_toast_manager(None)

        result = toast.get_toast_manager()
        assert result is not None
        assert isinstance(result, toast.ToastManager)

    def test_show_toast_function_returns_none_without_manager(self, qapp):
        """Test show_toast returns None without manager initialized."""
        from localmind.ui import toast

        # Reset global state
        toast._toast_manager = None

        result = toast.show_toast("Test message")
        assert result is None

    def test_show_toast_function_returns_notification_with_manager(self, qapp):
        """Test show_toast returns notification with manager initialized."""
        from localmind.ui import toast

        # Reset and initialize
        toast._toast_manager = None
        toast.init_toast_manager(None)

        result = toast.show_toast("Test message", duration=0)
        assert result is not None
        assert isinstance(result, toast.ToastNotification)


class TestToastActionCallback:
    """Tests for toast action callback functionality."""

    def test_action_callback_stored(self, qapp):
        """Test action callback is stored."""
        from localmind.ui.toast import ToastNotification, ToastType

        callback = MagicMock()
        toast = ToastNotification(
            "Test", ToastType.INFO, action_text="Click", action_callback=callback, duration=0
        )

        assert toast._action_callback is callback

    def test_on_action_clicked_calls_callback(self, qapp):
        """Test _on_action_clicked calls the callback."""
        from localmind.ui.toast import ToastNotification, ToastType

        callback = MagicMock()
        toast = ToastNotification(
            "Test", ToastType.INFO, action_text="Click", action_callback=callback, duration=0
        )

        toast._on_action_clicked()

        callback.assert_called_once()

    def test_action_callback_none_safe(self, qapp):
        """Test _on_action_clicked is safe with None callback."""
        from localmind.ui.toast import ToastNotification, ToastType

        toast = ToastNotification("Test", ToastType.INFO, duration=0)
        toast._action_callback = None

        # Should not raise
        toast._on_action_clicked()
