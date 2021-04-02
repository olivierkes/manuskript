#!/usr/bin/env python
# --!-- coding: utf8 --!--

from manuskript.ui.searchMenu import searchMenu
from manuskript.enums import Outline, Character, FlatData, World, Plot, PlotStep, Model
from manuskript.searchLabels import PLOT_STEP_COLUMNS_OFFSET


def triggerFilter(filterKey, actions):
    list(filter(lambda action: action.data() == filterKey, actions))[0].trigger()


def test_searchMenu_defaultColumns():
    """
    By default all model columns are selected.
    """
    search_menu = searchMenu()

    assert set(search_menu.columns(Model.Outline)) == {
        Outline.title, Outline.text, Outline.summaryFull,
        Outline.summarySentence, Outline.notes, Outline.POV,
        Outline.status, Outline.label
    }

    assert set(search_menu.columns(Model.Character)) == {
        Character.name, Character.motivation, Character.goal, Character.conflict,
        Character.epiphany, Character.summarySentence, Character.summaryPara,
        Character.summaryFull, Character.notes, Character.infos
    }

    assert set(search_menu.columns(Model.FlatData)) == {
        FlatData.summarySituation, FlatData.summarySentence, FlatData.summaryPara,
        FlatData.summaryPage, FlatData.summaryFull
    }

    assert set(search_menu.columns(Model.World)) == {
        World.name, World.description, World.passion, World.conflict
    }

    assert set(search_menu.columns(Model.Plot)) == {
        Plot.name, Plot.description, Plot.characters, Plot.result,
        Plot.summary, PLOT_STEP_COLUMNS_OFFSET + PlotStep.meta
    }


def test_searchMenu_someColumns():
    """
    When deselecting some filters the columns associated to those filters are not returned.
    """
    search_menu = searchMenu()

    triggerFilter(Model.Outline, search_menu.actions())
    triggerFilter(Model.Character, search_menu.actions())

    assert set(search_menu.columns(Model.Outline)) == set()
    assert set(search_menu.columns(Model.Character)) == set()
