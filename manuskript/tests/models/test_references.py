#!/usr/bin/env python
# --!-- coding: utf8 --!--

"""Tests for references.py"""

import pytest

def test_references(MWSampleProject):
    """
    Tests references using sample project.
    """
    from manuskript.models import references as Ref
    MW = MWSampleProject

    # References
    ref1 = Ref.plotReference("42", searchable=True)
    ref2 = Ref.plotReference("42")
    assert ref1 in ref2

    ref1 = Ref.characterReference("42", searchable=True)
    ref2 = Ref.characterReference("42")
    assert ref1 in ref2

    ref1 = Ref.textReference("42", searchable=True)
    ref2 = Ref.textReference("42")
    assert ref1 in ref2

    ref1 = Ref.worldReference("42", searchable=True)
    ref2 = Ref.worldReference("42")
    assert ref1 in ref2

    # Plots
    mdlPlots = MW.mdlPlots
    plotsImp = mdlPlots.getPlotsByImportance()
    plots = []
    [plots.extend(i) for i in plotsImp]
    assert len(plots) == 3
    plotID = plots[0]
    assert "\n" in Ref.infos(Ref.plotReference(plotID))
    assert "Not a ref" in Ref.infos("<invalid>")
    assert "Unknown" in Ref.infos(Ref.plotReference("999"))
    assert Ref.shortInfos(Ref.plotReference(plotID)) is not None
    assert Ref.shortInfos(Ref.plotReference("999")) == None
    assert Ref.shortInfos("<invalidref>") == -1

    # Character
    mdlChar = MW.mdlCharacter
    IDs = [mdlChar.ID(r) for r in range(mdlChar.rowCount())]
    assert len(IDs) == 6  # Peter, Paul, Philip, Stephen, Barnabas, Herod
    charID = IDs[0]
    assert "\n" in Ref.infos(Ref.characterReference(charID))
    assert "Unknown" in Ref.infos(Ref.characterReference("999"))
    assert Ref.shortInfos(Ref.characterReference(charID)) is not None
    assert Ref.shortInfos(Ref.characterReference("999")) == None
    assert Ref.shortInfos("<invalidref>") == -1

    # Texts
    mdlOutline = MW.mdlOutline
    assert mdlOutline.rowCount() == 3  # Jerusalem, Samaria, Extremities
    root = mdlOutline.rootItem
    textID = root.child(0).ID()

    assert "\n" in Ref.infos(Ref.textReference(textID))
    assert "Unknown" in Ref.infos(Ref.textReference("999"))
    assert Ref.shortInfos(Ref.textReference(textID)) is not None
    assert Ref.shortInfos(Ref.textReference("999")) == None
    assert Ref.shortInfos("<invalidref>") == -1

    # World
    mdlWorld = MW.mdlWorld
    assert mdlWorld.rowCount() == 3  # Places, Culture, Travel
    worldID = mdlWorld.itemID(mdlWorld.item(2).child(1))

    assert "\n" in Ref.infos(Ref.worldReference(worldID))
    assert "Unknown" in Ref.infos(Ref.worldReference("999"))
    assert Ref.shortInfos(Ref.worldReference(worldID)) is not None
    assert Ref.shortInfos(Ref.worldReference("999")) == None
    assert Ref.shortInfos("<invalidref>") == -1

    refs = [Ref.plotReference(plotID),
            Ref.characterReference(charID),
            Ref.textReference(textID),
            Ref.worldReference(worldID),]

    # Titles
    for ref in refs:
        assert Ref.title(ref) is not None
    assert Ref.title("<invalid>") is None
    assert Ref.title(Ref.plotReference("999")) is None

    # Other stuff
    assert Ref.type(Ref.plotReference(plotID)) == Ref.PlotLetter
    assert Ref.ID(Ref.textReference(textID)) == textID
    assert "Unknown" in Ref.tooltip(Ref.worldReference("999"))
    assert "Not a ref" in Ref.tooltip("<invalid>")
    for ref in refs:
        assert Ref.tooltip(ref) is not None

    # Links
    assert Ref.refToLink("<invalid>") is None
    assert Ref.refToLink(Ref.plotReference("999")) == Ref.plotReference("999")
    assert Ref.refToLink(Ref.characterReference("999")) == Ref.characterReference("999")
    assert Ref.refToLink(Ref.textReference("999")) == Ref.textReference("999")
    assert Ref.refToLink(Ref.worldReference("999")) == Ref.worldReference("999")
    for ref in refs:
        assert "<a href" in Ref.refToLink(ref)

    # Open
    assert Ref.open("<invalid>") is None
    assert Ref.open(Ref.plotReference("999")) == False
    assert Ref.open(Ref.characterReference("999")) == False
    assert Ref.open(Ref.textReference("999")) == False
    assert Ref.open(Ref.worldReference("999")) == False
    for ref in refs:
        assert Ref.open(ref) == True
    assert Ref.open(Ref.EmptyRef.format("Z", 14, "")) == False
