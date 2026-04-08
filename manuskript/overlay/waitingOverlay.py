import gi

from gi.repository import Gtk, Gdk

class WaitingOverlay:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file("ui/overlay/waiting_overlay.glade")

        self.widget: Gtk.Box = self.builder.get_object("waiting_overlay_root")
        self.spinnerAndLabel: Gtk.Box = self.builder.get_object("overlay_spinner_and_label")
        self.label: Gtk.Label = self.builder.get_object("overlay_label")

        ctx = self.spinnerAndLabel.get_style_context()
        color = ctx.lookup_color("theme_bg_color")[1]
        color.alpha = 0.5 

        css = f"""
        .loading-overlay {{
            background-color: rgba({int(color.red*255)}, {int(color.green*255)}, {int(color.blue*255)}, {color.alpha}); 
        }}
        .loading-overlay-spinner-and-label {{
            background-color: rgba(45, 45, 45, 0.8);
            color: rgba(255, 255, 255, 1);
            font-weight: bold;
        }}
        """

        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.widget.get_style_context().add_class("loading-overlay")

        self.spinnerAndLabel.get_style_context().add_class("loading-overlay-spinner-and-label")

        self.label.set_text("Please wait while data is loading...")

    def getWidget(self):
        return self.widget