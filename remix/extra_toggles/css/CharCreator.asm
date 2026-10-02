// Exposes saved Character Creator recipes per player on VS/Training CSS.
define LABEL("Custom Build")
constant VALUE_TYPE(CharacterSelectDebugMenu.value_type.STRING)
constant MIN_VALUE(0)
constant MAX_VALUE(4)
constant DEFAULT_VALUE(0)
// bitmask: [vs] [1p] [training] [bonus1] [bonus2] [allstar]
constant APPLIES_TO(0b101000)
// bitmask: [human] [cpu]
constant APPLIES_TO_HUMAN_CPU(0b11)
constant VALUE_ARRAY_POINTER(CharCreator.selected_builds)
constant ONCHANGE_HANDLER(CharCreator.on_build_changed_)
constant DISABLES_HIGH_SCORES(OS.TRUE)

string_table:
dw string_off
dw Toggles.head_char_creator_slot_1 + 0x0028
dw Toggles.head_char_creator_slot_2 + 0x0028
dw Toggles.head_char_creator_slot_3 + 0x0028
dw Toggles.head_char_creator_slot_4 + 0x0028

string_off:; String.insert("Off")
