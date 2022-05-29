# SetPreviewLayer
## DESCRIPTION
A utility script that allows you to set the preview layer for the specified glyph in the text editor (in all or selected text in tab). 

Troubles may arise in edge cases as they haven't been tested and this is my first Python script. It should be fully functional if your use cases are normal.

## INSTRUCTIONS
- **Selected Glyph**: the glyph in view or selected text that you wish to set the preview layer for. Changes in the editor aren't tracked and updates should be done manually with the ↺ button.
- **Preview Layer**: the preview layer of the selected glyph that you wish to change to. Changes in the glyph layers aren't tracked and updates should be done manually with the ↺ button.
- **Replace Selected Text**: if selected, the dropdown list of glyphs will only include ones in the selected text in the current tab, and replacements will only be performed on the selected text. Otherwise, it will be done on all texts in the current tab.
- **Change**: set the preview layer of the specified glyph to the selected layer.
- **Revert**: Becomes active after setting preview layers. Its function is to revert the most recent changes to their previous state. If the text in the editor or the layers in the last selected glyph have been changed after the last time you set preview layers, the reversion will fail.

## ACKNOWLEDGEMENT
Thanks for coding help from Rainer Scheichelbauer and Georg Seifert on Glyphs Forum. Many pieces of code in this script also used the [mekkablue script](https://github.com/mekkablue/Glyphs-Scripts) as reference.

