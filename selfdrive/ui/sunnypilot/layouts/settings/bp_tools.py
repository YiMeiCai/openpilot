"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.common.params import Params
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr, tr_noop
from openpilot.system.ui.sunnypilot.widgets.list_view import toggle_item_sp, option_item_sp
from openpilot.system.ui.widgets.scroller_tici import Scroller
from openpilot.system.ui.widgets import Widget

ROLL_WARN_DESCRIPTION = tr_noop("A red flashing alert will be shown when the vehicle creeps forward at low speed " +
                                "towards the lead vehicle." +
                                "<br>Note: This alert is only designed as a notification. " +
                                "It is the driver's responsibility to keep the vehicle under control at all times.")

# Both params are INT: distance in decimetres (10 -> 1.0 m), speed in km/h
ROLL_WARN_DIST_MIN, ROLL_WARN_DIST_MAX, ROLL_WARN_DIST_STEP = 10, 100, 5
ROLL_WARN_VMAX_MIN, ROLL_WARN_VMAX_MAX, ROLL_WARN_VMAX_STEP = 3, 30, 1

# Migrate values written by the old 3-button selector (stored 0/1/2)
_LEGACY_DIST = (20, 35, 50)
_LEGACY_VMAX = (5, 10, 15)


class BPToolsLayout(Widget):
  """Scratch panel for locally added features. New beta items go here first."""

  def __init__(self):
    super().__init__()

    self._params = Params()
    self._migrate_legacy_params()
    items = self._initialize_items()
    self._scroller = Scroller(items, line_separator=True, spacing=0)

  def _migrate_legacy_params(self):
    """Convert legacy selector indices into real units. Idempotent."""
    try:
      dist = int(float(self._params.get("LeadRollWarnDist", return_default=True)))
      if dist < ROLL_WARN_DIST_MIN:
        self._params.put("LeadRollWarnDist", _LEGACY_DIST[max(0, min(dist, 2))])
    except Exception:
      pass
    try:
      vmax = int(float(self._params.get("LeadRollWarnVmax", return_default=True)))
      if vmax < ROLL_WARN_VMAX_MIN:
        self._params.put("LeadRollWarnVmax", _LEGACY_VMAX[max(0, min(vmax, 2))])
    except Exception:
      pass

  def _initialize_items(self):
    self._roll_warn_toggle = toggle_item_sp(
      title=lambda: tr("Low Speed Roll Warning (Beta)"),
      description=ROLL_WARN_DESCRIPTION,
      param="LeadRollWarnEnabled",
      initial_state=ui_state.params.get_bool("LeadRollWarnEnabled"),
    )
    self._roll_warn_dist = option_item_sp(
      title=lambda: tr("Roll Warning Distance"),
      description=lambda: tr("Lead vehicle distance below which the alert is shown."),
      param="LeadRollWarnDist",
      min_value=ROLL_WARN_DIST_MIN,
      max_value=ROLL_WARN_DIST_MAX,
      value_change_step=ROLL_WARN_DIST_STEP,
      label_callback=lambda v: f"{v / 10:.1f} m",
      inline=False,
    )
    self._roll_warn_vmax = option_item_sp(
      title=lambda: tr("Roll Warning Speed Limit"),
      description=lambda: tr("Only trigger the alert below this speed."),
      param="LeadRollWarnVmax",
      min_value=ROLL_WARN_VMAX_MIN,
      max_value=ROLL_WARN_VMAX_MAX,
      value_change_step=ROLL_WARN_VMAX_STEP,
      label_callback=lambda v: f"{v} km/h",
      inline=False,
    )
    self._reverse_cam_toggle = toggle_item_sp(
      title=lambda: tr("Driver Camera On Reverse"),
      description=lambda: tr("Automatically show the driver monitoring camera on the driving screen " +
                             "while the gear is in reverse."),
      param="ReverseDriverCamEnabled",
      initial_state=ui_state.params.get_bool("ReverseDriverCamEnabled"),
    )

    return [
      self._roll_warn_toggle,
      self._roll_warn_dist,
      self._roll_warn_vmax,
      self._reverse_cam_toggle,
    ]

  @staticmethod
  def _sync_option(action_item, key: str):
    """Pull a foreign param change into the +/- control."""
    try:
      value = int(float(ui_state.params.get(key, return_default=True)))
      if action_item.get_value() != value:
        action_item.set_value(value)
    except Exception:
      pass

  def _update_state(self):
    super()._update_state()

    try:
      self._roll_warn_toggle.action_item.set_state(self._params.get_bool("LeadRollWarnEnabled"))
      self._sync_option(self._roll_warn_dist.action_item, "LeadRollWarnDist")
      self._sync_option(self._roll_warn_vmax.action_item, "LeadRollWarnVmax")
      self._reverse_cam_toggle.action_item.set_state(self._params.get_bool("ReverseDriverCamEnabled"))
    except Exception:
      pass

  def _render(self, rect):
    self._scroller.render(rect)

  def show_event(self):
    self._scroller.show_event()
