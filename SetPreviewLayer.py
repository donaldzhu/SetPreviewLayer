# MenuTitle: Set Preview Layer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
import vanilla
__doc__ = """
Set preview layer for all instances of a glyph
"""


class SetPreviewLayer(object):

    def __init__(self):
      textMargin = 2
      textW = 120
      textH = 20
      boxW = 200
      boxH = textH + 4
      resetW = textH
      resetH = textH
      resetMargin = 6
      btnW = 80
      checkBoxW = textW + boxW
      
      textLeft = 15
      boxLeft = textW + textLeft
      resetLeft = boxW + boxLeft + resetMargin
      lineHeight = textH + 10
      top = 12

      windowW = textLeft * 2 + textW + boxW + resetW + resetMargin
      windowH = top + boxH * 3 + lineHeight * 2 

      # glyph
      self.uniqGlyphs = [] # the current list of unique glyphs in edit view/selected text
      self.currentGlyph = None # the currently chosen glyph in the dropdown
      self.glyphCallbackEnabled = True # to disable unintended vanilla callbacks

      # layer
      self.currentLayer = None # the currently chosen layer in the dropdown
      self.layers = [] # the current list of layers in the current glyph
      self.layerIds = [] # the current list of layers ids (stored separately as layers are referenced and won't be static) 

      # use selected
      self.useSelected = False # if we use the selected text in the current tab or not

      # revert
      self.lastGlyph = None # the last glyph that was changed
      self.lastGlyphLayerIds =  [] # the layer ids of the last changed glyph
      self.lastText = '' # the text that the change was performed on
      self.lastLayers = [] # the list of layers to revert to for the selected glyph (as the unchanged state could consist of a mix of layers)
      self.lastUseSelected = False # if the last changed was done on selected text only
      self.lastTextCursor = None # stores the text cursor position when the last change was performed
      self.lastTextRange = None # stores the text range when the last change was performed 

      ################ UI ################
      # dropdowns
      self.w = vanilla.FloatingWindow(
          (windowW, windowH),
          'Set Preview Layer',
          autosaveName='com.donaldzhu.SetPreviewLayer.mainwindow'
      )

      self.w.text1 = vanilla.TextBox(
        (textLeft, top + textMargin, textW, textH),
        'Set preview of'
      )

      self.w.glyphsDropdown = vanilla.ComboBox(
        (boxLeft, top, boxW, boxH),
        self.GetGlyphs(),
        callback=self.OnSelectGlyph
      )

      self.w.glyphsReset = vanilla.SquareButton(
        (resetLeft, top + textMargin, resetW, resetH),
        '↺', 
        callback=self.UpdateGlyphs
      )

      top += lineHeight

      self.w.text2 = vanilla.TextBox(
        (textLeft, top + textMargin, textW, textH),
        'to the layer'
      )

      self.w.layersDropdown = vanilla.PopUpButton(
        (boxLeft, top, boxW, boxH),
        self.GetLayers(),
        callback=self.OnSelectLayer
      )

      self.w.layersReset = vanilla.SquareButton(
        (resetLeft, top + textMargin, resetW, resetH),
        '↺' ,
        callback=self.UpdateLayers 
      )

      # checkbox
      top += lineHeight

      self.w.useSelected = vanilla.CheckBox(
        (textLeft, top, checkBoxW, boxH),
        'Replace selected text',
        callback=self.OnToggleUseSelected
      )

      # buttons
      top += lineHeight

      self.w.revertButton = vanilla.Button(
        (textLeft, top, btnW, boxH),
        'Revert',
        callback=self.RevertPreviewLayer
      )

      self.w.changeButton = vanilla.Button(
        (textW + boxW - btnW, top, btnW, boxH),
        'Change',
        callback=self.SetPreviewLayer
      )
      
      self.w.open()
      self.w.revertButton.enable(False)

      # loads last stored preferences
      if not self.LoadPreferences():
        print('⚠️ Note: Could not load preferences.')
    
    ################ GLYPH ################
    # returns the unique glyphs in a provided list
    def GetUniqGlyphsInList(self, layers):
      glyphList = list({g.parent.name for g in layers})
      if None in glyphList: glyphList.remove(None)
      return glyphList

    # returns the unique glyphs in the current tab or selceted text 
    def GetGlyphs(self):
      font = Glyphs.font
      tab = font.currentTab if font else None
      useSelected = self.useSelected

      if not tab: 
        self.uniqGlyphs = []
      else:
        layers = list(tab.selectedLayers if useSelected else tab.layers)
        self.uniqGlyphs = self.GetUniqGlyphsInList(layers)
        self.uniqGlyphs.sort(key=lambda _g: list(g.name for g in font.glyphs).index(_g))
      
      return self.uniqGlyphs

    # updates the glyph dropdown list
    def UpdateGlyphs(self, _=None):      
      glyphsDropdown = self.w.glyphsDropdown

      self.GetGlyphs() # updates self.uniqGlyphs

      self.glyphCallbackEnabled = False # toggles callback as `setItems` will trigger callback unintentionally
      glyphsDropdown.setItems(self.uniqGlyphs) # updates the glyph dropdown list
      
      # if the current glyph is not in the update list, discard it
      if self.currentGlyph not in self.uniqGlyphs:
        self.currentGlyph = None

      glyphsDropdown.set(self.currentGlyph)
      self.glyphCallbackEnabled = True
      self.OnSelectGlyph(glyphsDropdown) # manually invokes callback

    # glyph dropdown callback
    def OnSelectGlyph(self, sender):
      if not self.glyphCallbackEnabled: return
      currentGlyph = sender.get()

      # in case the user enters a glyph that isn't in view (i.e. through keyboard input)
      if currentGlyph not in self.uniqGlyphs:
        currentGlyph = None
        sender.set(currentGlyph)
      self.currentGlyph = currentGlyph
      self.UpdateLayers()
      self.SavePreference('glyph', currentGlyph)

    ################ LAYER ################
    # returns the layers in the current glyph 
    def GetLayers(self):
      font = Glyphs.font
      glyph = font.glyphs[self.currentGlyph] if (self.currentGlyph and font) else None

      self.layers = list(glyph.layers) if glyph else []
      self.layerIds = [l.layerId for l in self.layers]
      return [l.name for l in self.layers]

    # updates the layer dropdown list
    def UpdateLayers(self, _=None):
      lastLayer = self.currentLayer # stores the last layer because `setItems` invokes callback and clears self.currentLayer
      layersDropdown = self.w.layersDropdown
      newLayerNames = self.GetLayers()

      layersDropdown.setItems(newLayerNames)
      index = 0 # by default chooses the first one in list

      # checks if the last chosen layer id is in the updated list
      if lastLayer and lastLayer.layerId in self.layerIds:
        index = self.layerIds.index(lastLayer.layerId)
        self.currentLayer = lastLayer

      layersDropdown.set(index)
      self.OnSelectLayer(layersDropdown)

    # layer dropdown callback
    def OnSelectLayer(self, sender):
      dropdownIndex = sender.get()
      layerLength = len(self.layers)

      # the index could be out of bounds due to stale data
      layerExists = layerLength > dropdownIndex and dropdownIndex != -1
      index = dropdownIndex if layerExists else 0
      self.currentLayer = self.layers[index] if layerLength else None
      layerId = self.currentLayer.layerId if self.currentLayer else None
      self.SavePreference('layer', layerId)
    
    ################ SELECT ################
    # useSelected checkbox callback
    def OnToggleUseSelected(self, sender):
      self.useSelected = sender.get()
      self.SavePreference('useSelected', self.useSelected)
    
    ################ SET ################
    # main function
    def SetPreviewLayer(self, _):
      font = Glyphs.font
      tab = font.currentTab if font else None
      currentGlyph = self.currentGlyph
      currentLayer = self.currentLayer

      if not tab: return
      
      exceptionMessage = 'Attempt to set glyph "%s" to layer "%s" failed -' % (currentGlyph, currentLayer.name) 
      
      # check if the operation could be performed (in case of incompatible stale data)
      self.UpdateGlyphs()
      if currentGlyph not in self.uniqGlyphs:
        return self.LogException(exceptionMessage + 'glyph not found in current %s.' % 'tab' if self.useSelected else 'selection')
      
      self.UpdateLayers()
      if currentLayer.layerId not in self.layerIds:
        return self.LogException(exceptionMessage + 'layer not found in glyph.')

      newLayers = []
      tabLayers = list(tab.layers)
      self.lastLayers = [] # restore to default state
      self.lastTextCursor = tab.textCursor
      self.lastTextRange = tab.textRange
      self.lastUseSelected = self.useSelected

      # loop through all layers in current tab
      for i in range(len(tabLayers)):
        l = tabLayers[i]

        # inserts the chosen layer instead of the layer belongs to the current glyph
        # if useSelected = True, check if the index is within the selection range
        if l.parent.name == currentGlyph and (
          not self.useSelected or self.IsSelected(i)
        ):
          self.lastLayers.append(l) # stores changed layers for later reversion
          l = currentLayer
        newLayers.append(l)
      
      self.w.revertButton.enable(True)
      self.lastGlyph = currentGlyph
      self.lastText = tab.text
      self.lastGlyphLayerIds = self.layerIds
      tab.layers = newLayers

    ################ REVERT ################
    # reverts last changes
    def RevertPreviewLayer(self, _):
      font = Glyphs.font
      tab = font.currentTab if font else None

      if not tab: return
      text = tab.text

      # aborts reversion if text has changed
      if self.lastText != text:
        self.LogException('Attempt to revert failed - text in current tab has changed')
        return self.DiscardRevert()

      # aborts reversion if the layers of the last changed glyph has changed    
      self.UpdateLayers()
      if set(self.layerIds) != set(self.lastGlyphLayerIds):
        self.LogException('Attempt to revert failed - layers in last changed glyph has changed')
        return self.DiscardRevert()
      
      newLayers = []
      layers = list(tab.layers)
      for i in range(len(layers)):
        l = layers[i]

        # inserts `self.lastLayers` back in order 
        # also checks if last change used selected only
        if l.parent.name == self.lastGlyph and (
          not self.lastUseSelected or self.IsSelected(i)
        ):
          l = self.lastLayers[0]
          self.lastLayers.pop(0)
        newLayers.append(l)

      tab.layers = newLayers
      self.DiscardRevert()
    
    # disables revert button and discards last changed data
    def DiscardRevert(self):
      self.lastGlyph = None
      self.lastGlyphLayerIds = []
      self.lastText = ''
      self.lastLayers = []
      self.w.revertButton.enable(False)

    ################ PREFENCES ################
    def SavePreference(self, suffix, value):
      try:        
        Glyphs.defaults['com.donaldzhu.SetPreviewLayer.%s' % suffix] = value
      except:
        import traceback
        print(traceback.format_exc())

    def GetPreference(self,suffix):
      try:
        return Glyphs.defaults['com.donaldzhu.SetPreviewLayer.%s' % suffix]
      except:
        import traceback
        print(traceback.format_exc())

    def LoadPreferences(self):
      font = Glyphs.font
      if not font: return

      try:
        glyph = self.GetPreference('glyph')
        layerId = self.GetPreference('layer')
        useSelected = self.GetPreference('useSelected')
        
        self.w.useSelected.set(useSelected)
        self.OnToggleUseSelected(self.w.useSelected)
        
        self.UpdateGlyphs()
        self.w.glyphsDropdown.set(glyph)
        self.OnSelectGlyph(self.w.glyphsDropdown)
      
        # if the last saved glyph is found and the last saved layerId still exists
        if self.currentGlyph:
          self.UpdateLayers()
          layerDropdown = self.w.layersDropdown
          if layerId in self.layerIds:
            index = self.layerIds.index(layerId)
            layerDropdown.set(index)
            self.OnSelectLayer(layerDropdown)
        return True
      except:
        import traceback
        print(traceback.format_exc())
        return False

    ################ UTIL ################
    def LogException(self, message):
      Glyphs.showNotification(
        '⚠️ Operation failed',
        message
      )
    
    # check if the given index is within the range of the selected text
    def IsSelected(self, index):
      endTextCursor = self.lastTextCursor + self.lastTextRange
      return self.lastTextCursor <= index < endTextCursor
      

SetPreviewLayer()
