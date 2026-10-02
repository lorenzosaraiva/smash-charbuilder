// Character Creator menu declarations.
// Included inside scope Toggles by character_appender.py.

head_char_creator:
cc_original_12_only:; Menu.entry("Original 12 Only", Menu.type.BOOL, OS.FALSE, 0, 1, OS.NULL, OS.NULL, Menu.bool_string_table, OS.NULL, cc_hub_slot_1)
cc_hub_slot_1:; Menu.entry_title("BUILD 1", show_char_creator_slot_1_, cc_hub_slot_2)
cc_hub_slot_2:; Menu.entry_title("BUILD 2", show_char_creator_slot_2_, cc_hub_slot_3)
cc_hub_slot_3:; Menu.entry_title("BUILD 3", show_char_creator_slot_3_, cc_hub_slot_4)
cc_hub_slot_4:; Menu.entry_title("BUILD 4", show_char_creator_slot_4_, OS.NULL)

// Layout is intentionally identical for every slot. Menu.export_/import_ pack
// each page into its own SRAM block. Name must be the first persisted entry:
// INPUT advances the serializer by 20 bytes and numeric values follow it.
macro char_creator_name_entry(slot, next) {
    dw Menu.type.INPUT
    dw 0
    dw 0
    dw 20
    dw toggle_edit_mode_
    dw OS.NULL
    dw OS.NULL
    dw {next}
    dw 0
    dw {slot}
    db "BUILD ", 0x30 + {slot}, 0x00
    fill 12
    OS.align(4)
}

macro char_creator_slot(slot, next_slot) {
    head_char_creator_slot_{slot}:; char_creator_name_entry({slot}, cc_slot_{slot}_enabled)
    cc_slot_{slot}_enabled:; Menu.entry("Enabled", Menu.type.BOOL, OS.FALSE, 0, 1, OS.NULL, OS.NULL, Menu.bool_string_table, OS.NULL, cc_slot_{slot}_body)
    cc_slot_{slot}_body:; Menu.entry("Body", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_copy_body)
    cc_slot_{slot}_copy_body:; Menu.entry_title_with_extra("USE BODY FOR ALL MOVES", CharCreator.copy_body_to_all_, {slot}, cc_slot_{slot}_jab)
    cc_slot_{slot}_jab:; Menu.entry("Jab", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dash)
    cc_slot_{slot}_dash:; Menu.entry("Dash Attack", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_ftilt)
    cc_slot_{slot}_ftilt:; Menu.entry("Forward Tilt", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_utilt)
    cc_slot_{slot}_utilt:; Menu.entry("Up Tilt", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dtilt)
    cc_slot_{slot}_dtilt:; Menu.entry("Down Tilt", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_fsmash)
    cc_slot_{slot}_fsmash:; Menu.entry("Forward Smash", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_usmash)
    cc_slot_{slot}_usmash:; Menu.entry("Up Smash", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dsmash)
    cc_slot_{slot}_dsmash:; Menu.entry("Down Smash", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_nair)
    cc_slot_{slot}_nair:; Menu.entry("Neutral Air", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_fair)
    cc_slot_{slot}_fair:; Menu.entry("Forward Air", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_bair)
    cc_slot_{slot}_bair:; Menu.entry("Back Air", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_uair)
    cc_slot_{slot}_uair:; Menu.entry("Up Air", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dair)
    cc_slot_{slot}_dair:; Menu.entry("Down Air", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_nsp)
    cc_slot_{slot}_nsp:; Menu.entry("Neutral Special", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_usp)
    cc_slot_{slot}_usp:; Menu.entry("Up Special", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dsp)
    cc_slot_{slot}_dsp:; Menu.entry("Down Special", Menu.type.INT, 0, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_test)
    cc_slot_{slot}_test:; Menu.entry_title_with_extra("TEST IN TRAINING", CharCreator.test_in_training_, {slot}, OS.NULL)
}

char_creator_slot(1, 2)
char_creator_slot(2, 3)
char_creator_slot(3, 4)
char_creator_slot(4, 0)
