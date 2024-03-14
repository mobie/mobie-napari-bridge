# launch_napari.py
from napari import Viewer, run
import sys
import os
import yaml

module0 = "mobie-napari-bridge"

module = module0.replace("-", "_")

def get_widgetname():
    widget_name = None
    if len(sys.argv) > 1:
        if sys.argv[1] != "":
            selection = sys.argv[1]
            with open(os.path.join(os.getcwd(), "src", module, "napari.yaml")) as f:
                mod_settings = yaml.safe_load(f)

            for cmd in mod_settings['contributions']['commands']:
                if selection not in cmd['python_name']:
                    continue
                else:
                    w_id = cmd['id']
                    for widget in mod_settings['contributions']['widgets']:
                        if w_id not in widget['command']:
                            continue
                        else:
                            widget_name = widget['display_name']

    return widget_name




if __name__ == "__main__":

    viewer = Viewer()
    widget_name = get_widgetname()
    dock_widget, plugin_widget = viewer.window.add_plugin_dock_widget(
       module0, widget_name=widget_name
    )
    # Optional steps to setup your plugin to a state of failure
    # E.g. plugin_widget.parameter_name.value = "some value"
    # E.g. plugin_widget.button.click()
    run()