// Character Creator menu declarations.
// Included inside scope Toggles by character_appender.py.

head_char_creator:
cc_original_12_only:; Menu.entry("Original 12 Only", Menu.type.BOOL, OS.TRUE, 0, 1, OS.NULL, OS.NULL, Menu.bool_string_table, OS.NULL, cc_hub_slot_1)
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

// Four ready-to-play mixed recipes. Original-roster normals use compiled
// donor tables; Neutral Special defaults to the body's own move.
macro char_creator_slot(slot, next_slot, body, jab, dash, ftilt, utilt, dtilt, fsmash, usmash, dsmash, nair, fair, bair, uair, dair) {
    head_char_creator_slot_{slot}:; char_creator_name_entry({slot}, cc_slot_{slot}_enabled)
    cc_slot_{slot}_enabled:; Menu.entry("Enabled", Menu.type.BOOL, OS.TRUE, 0, 1, OS.NULL, OS.NULL, Menu.bool_string_table, OS.NULL, cc_slot_{slot}_body)
    cc_slot_{slot}_body:; Menu.entry("Body", Menu.type.INT, {body}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_copy_body)
    cc_slot_{slot}_copy_body:; Menu.entry_title_with_extra("USE BODY FOR ALL MOVES", CharCreator.copy_body_to_all_, {slot}, cc_slot_{slot}_jab)
    cc_slot_{slot}_jab:; Menu.entry("Jab", Menu.type.INT, {jab}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dash)
    cc_slot_{slot}_dash:; Menu.entry("Dash Attack", Menu.type.INT, {dash}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_ftilt)
    cc_slot_{slot}_ftilt:; Menu.entry("Forward Tilt", Menu.type.INT, {ftilt}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_utilt)
    cc_slot_{slot}_utilt:; Menu.entry("Up Tilt", Menu.type.INT, {utilt}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dtilt)
    cc_slot_{slot}_dtilt:; Menu.entry("Down Tilt", Menu.type.INT, {dtilt}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_fsmash)
    cc_slot_{slot}_fsmash:; Menu.entry("Forward Smash", Menu.type.INT, {fsmash}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_usmash)
    cc_slot_{slot}_usmash:; Menu.entry("Up Smash", Menu.type.INT, {usmash}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dsmash)
    cc_slot_{slot}_dsmash:; Menu.entry("Down Smash", Menu.type.INT, {dsmash}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_nair)
    cc_slot_{slot}_nair:; Menu.entry("Neutral Air", Menu.type.INT, {nair}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_fair)
    cc_slot_{slot}_fair:; Menu.entry("Forward Air", Menu.type.INT, {fair}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_bair)
    cc_slot_{slot}_bair:; Menu.entry("Back Air", Menu.type.INT, {bair}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_uair)
    cc_slot_{slot}_uair:; Menu.entry("Up Air", Menu.type.INT, {uair}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dair)
    cc_slot_{slot}_dair:; Menu.entry("Down Air", Menu.type.INT, {dair}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_grab)
    cc_slot_{slot}_grab:; Menu.entry("Grab", Menu.type.INT, {body}, 0, 11, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_throwf)
    cc_slot_{slot}_throwf:; Menu.entry("Forward Throw", Menu.type.INT, {body}, 0, 11, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_throwb)
    cc_slot_{slot}_throwb:; Menu.entry("Back Throw", Menu.type.INT, {body}, 0, 11, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_nsp)
    cc_slot_{slot}_nsp:; Menu.entry("Neutral Special", Menu.type.MAX1, 0, 0, 12, OS.NULL, OS.NULL, CharCreator.neutral_string_tables + ({slot} - 1) * 52, OS.NULL, cc_slot_{slot}_usp)
    cc_slot_{slot}_usp:; Menu.entry("Up Special", Menu.type.INT, {body}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_dsp)
    cc_slot_{slot}_dsp:; Menu.entry("Down Special", Menu.type.INT, {body}, 0, CharCreatorCatalog.COUNT - 1, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_taunt)
    cc_slot_{slot}_taunt:; Menu.entry("Taunt", Menu.type.MAX1, {body}, 0, 11, OS.NULL, OS.NULL, CharCreatorCatalog.string_table, OS.NULL, cc_slot_{slot}_test)
    cc_slot_{slot}_test:; Menu.entry_title_with_extra("TEST IN TRAINING", CharCreator.test_in_training_, {slot}, OS.NULL)
}

// body, then Jab through Down Air (catalog order starts Mario, Fox, DK...).
char_creator_slot(1, 2, 0, 1, 7, 5, 3, 6, 2, 3, 7, 6, 5, 1, 2, 7)
char_creator_slot(2, 3, 1, 0, 2, 4, 3, 5, 7, 0, 2, 4, 5, 7, 3, 0)
char_creator_slot(3, 4, 5, 9, 6, 0, 3, 1, 8, 9, 6, 0, 3, 1, 8, 9)
char_creator_slot(4, 0, 8, 4, 7, 5, 2, 11, 1, 4, 7, 5, 2, 11, 1, 4)
