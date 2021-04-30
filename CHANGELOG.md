# Changelog

## [0.12.0](https://github.com/olivierkes/manuskript/tree/0.12.0) (2021-04-30)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.11.0...HEAD)

**Implemented enhancements:**

- Improving user-friendliness of log files [\#852](https://github.com/olivierkes/manuskript/issues/852)
- \[Feature Request\] Add spell check for Chinese. [\#822](https://github.com/olivierkes/manuskript/issues/822)
- Number of characters instead of number of words? [\#774](https://github.com/olivierkes/manuskript/issues/774)
- Italian spellchecker [\#730](https://github.com/olivierkes/manuskript/issues/730)
- \[Feature Request\] Word counter in full screen mode [\#723](https://github.com/olivierkes/manuskript/issues/723)
- Word count statistics incorrect when using Chinese characters [\#607](https://github.com/olivierkes/manuskript/issues/607)
- select which monitor in full screen mode [\#456](https://github.com/olivierkes/manuskript/issues/456)
- \[feature request\] Scene Search [\#376](https://github.com/olivierkes/manuskript/issues/376)
- \[Feature request\] References in characters' bios [\#347](https://github.com/olivierkes/manuskript/issues/347)
- add languagetool [\#142](https://github.com/olivierkes/manuskript/issues/142)

**Fixed bugs:**

- Using a world building template is broken [\#866](https://github.com/olivierkes/manuskript/issues/866)
- Slow startup when using language\_tool\_python in the test python setup [\#862](https://github.com/olivierkes/manuskript/issues/862)
- When using the + on editor or outline the application crashes [\#855](https://github.com/olivierkes/manuskript/issues/855)
- Fullscreen and Exit -\> Fullscreen survives [\#846](https://github.com/olivierkes/manuskript/issues/846)
- Loading another project leads to crash [\#833](https://github.com/olivierkes/manuskript/issues/833)
- Crashes with using language-check [\#832](https://github.com/olivierkes/manuskript/issues/832)
- Crash on showing settingsWindow.py [\#817](https://github.com/olivierkes/manuskript/issues/817)
- Python syntax warning upon installation [\#792](https://github.com/olivierkes/manuskript/issues/792)
- Right click → Insert Reference buggy when search term is followed by punctuation [\#781](https://github.com/olivierkes/manuskript/issues/781)
- Can't open any file [\#758](https://github.com/olivierkes/manuskript/issues/758)
- Error on export when using pandoc [\#736](https://github.com/olivierkes/manuskript/issues/736)
- Snap Package: All types of export with pandoc fail with error 97 [\#709](https://github.com/olivierkes/manuskript/issues/709)
- Main major and minor character are not functional [\#698](https://github.com/olivierkes/manuskript/issues/698)
- export error \(pandoc\) [\#590](https://github.com/olivierkes/manuskript/issues/590)

**Closed issues:**

- Small bug with LanguageTool [\#860](https://github.com/olivierkes/manuskript/issues/860)
- Help! Can't open MSK.file [\#759](https://github.com/olivierkes/manuskript/issues/759)
- Can't run Manuskript [\#742](https://github.com/olivierkes/manuskript/issues/742)
- Manuskript Crashes on Project Open [\#741](https://github.com/olivierkes/manuskript/issues/741)
- Program crashes randomly and then never opens again even after reinstall [\#665](https://github.com/olivierkes/manuskript/issues/665)
- PLOT Character Error Message [\#519](https://github.com/olivierkes/manuskript/issues/519)
- Program crashes on copy and paste [\#441](https://github.com/olivierkes/manuskript/issues/441)
- Enable/Disable POV-Option for Characters [\#335](https://github.com/olivierkes/manuskript/issues/335)
- Show character count progress indicator [\#334](https://github.com/olivierkes/manuskript/issues/334)

**Merged pull requests:**

- Fix missing root when using world building template [\#867](https://github.com/olivierkes/manuskript/pull/867) ([belug23](https://github.com/belug23))
- Add configuration for github actions to test linux on pull requests [\#864](https://github.com/olivierkes/manuskript/pull/864) ([belug23](https://github.com/belug23))
- Fix errors when language tool isn't installed [\#863](https://github.com/olivierkes/manuskript/pull/863) ([belug23](https://github.com/belug23))
- Fix 860 languagetool get locale language [\#861](https://github.com/olivierkes/manuskript/pull/861) ([belug23](https://github.com/belug23))
- Friendly logging for end users [\#859](https://github.com/olivierkes/manuskript/pull/859) ([worstje](https://github.com/worstje))
- Fixing the tests for travis-CI [\#858](https://github.com/olivierkes/manuskript/pull/858) ([belug23](https://github.com/belug23))
- Fix \#855 - Avoid a crash when there's no model [\#856](https://github.com/olivierkes/manuskript/pull/856) ([belug23](https://github.com/belug23))
- Fix \#846 close Fullscreen when exiting main editor [\#854](https://github.com/olivierkes/manuskript/pull/854) ([belug23](https://github.com/belug23))
- Fix \#456 - Force the distraction free window on the display of the main window [\#851](https://github.com/olivierkes/manuskript/pull/851) ([belug23](https://github.com/belug23))
- Fixed project not opening with missing background [\#850](https://github.com/olivierkes/manuskript/pull/850) ([rbb8403](https://github.com/rbb8403))
- setup signal handler to avoid accident data loss [\#835](https://github.com/olivierkes/manuskript/pull/835) ([lingsamuel](https://github.com/lingsamuel))
- Properly disconnect add person connection. [\#834](https://github.com/olivierkes/manuskript/pull/834) ([BentleyJOakes](https://github.com/BentleyJOakes))
- Change outlineItem ID assignment process for major optimization [\#827](https://github.com/olivierkes/manuskript/pull/827) ([emgineering](https://github.com/emgineering))
- Fix for TypeErrors when using certain app styles [\#793](https://github.com/olivierkes/manuskript/pull/793) ([FrancoisDuchene](https://github.com/FrancoisDuchene))
- Fixed pandoc command arguments [\#790](https://github.com/olivierkes/manuskript/pull/790) ([DarkRedman](https://github.com/DarkRedman))
- Update manuskript\_fr.ts [\#789](https://github.com/olivierkes/manuskript/pull/789) ([DarkRedman](https://github.com/DarkRedman))
- Update abstractModel.py [\#777](https://github.com/olivierkes/manuskript/pull/777) ([siliconserf](https://github.com/siliconserf))
- Clones importance setting when adding new characters. [\#775](https://github.com/olivierkes/manuskript/pull/775) ([BentleyJOakes](https://github.com/BentleyJOakes))
- typofixing here and there [\#768](https://github.com/olivierkes/manuskript/pull/768) ([goofy-mdn](https://github.com/goofy-mdn))
- Fix Python 3.8 SyntaxWarning: "is not" with a literal [\#762](https://github.com/olivierkes/manuskript/pull/762) ([gedakc](https://github.com/gedakc))
- Set minimum of xcode11 for macOS X in Travis CI build [\#760](https://github.com/olivierkes/manuskript/pull/760) ([gedakc](https://github.com/gedakc))
- Enabling/Disabling POV for a specific character [\#748](https://github.com/olivierkes/manuskript/pull/748) ([TheJackiMonster](https://github.com/TheJackiMonster))
- Added basic support for LanguageTool via 'language\_check' as advanced spellchecker [\#747](https://github.com/olivierkes/manuskript/pull/747) ([TheJackiMonster](https://github.com/TheJackiMonster))
- Added char-count with settings to enable/disable it. [\#746](https://github.com/olivierkes/manuskript/pull/746) ([TheJackiMonster](https://github.com/TheJackiMonster))
- Add snap layout for pandoc templates directory [\#737](https://github.com/olivierkes/manuskript/pull/737) ([tomwardill](https://github.com/tomwardill))
- Select newly added world items, opening branches as necessary [\#735](https://github.com/olivierkes/manuskript/pull/735) ([johnbintz](https://github.com/johnbintz))
- Add global search [\#717](https://github.com/olivierkes/manuskript/pull/717) ([moisesjbc](https://github.com/moisesjbc))
- added 3 buttons to the textEditView that allow quickly adding new items [\#690](https://github.com/olivierkes/manuskript/pull/690) ([nagolinc](https://github.com/nagolinc))
- Logging and command-line arguments [\#667](https://github.com/olivierkes/manuskript/pull/667) ([worstje](https://github.com/worstje))
- adding characters count. Implementing \#334 [\#339](https://github.com/olivierkes/manuskript/pull/339) ([lechbaczynski](https://github.com/lechbaczynski))

## [0.11.0](https://github.com/olivierkes/manuskript/tree/0.11.0) (2020-01-18)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.10.0...0.11.0)

**Implemented enhancements:**

- \[Feature Request\] Automatically calculate folder word count goal [\#664](https://github.com/olivierkes/manuskript/issues/664)

**Fixed bugs:**

- Ctrl+Space destroys and Ctrl+Z can't recover [\#703](https://github.com/olivierkes/manuskript/issues/703)
- References Mysteriously Delete in Summary and Reference/Notes Fields [\#688](https://github.com/olivierkes/manuskript/issues/688)
- After use of ctrl-z or ctrl-v Manuskript goes in inactive State [\#672](https://github.com/olivierkes/manuskript/issues/672)
- Cut and Paste - Comment Field - First shows, then disappiers [\#670](https://github.com/olivierkes/manuskript/issues/670)
- 0.10.0 crash using Windows dark mode [\#659](https://github.com/olivierkes/manuskript/issues/659)

**Closed issues:**

- Can't get the program to open [\#686](https://github.com/olivierkes/manuskript/issues/686)
- Default for separator between folders should be pagebreak [\#680](https://github.com/olivierkes/manuskript/issues/680)
- Program crashes on copy and paste [\#441](https://github.com/olivierkes/manuskript/issues/441)

**Merged pull requests:**

- Change wording of import warning for PyQt/Qt versions 5.11 and 5.12 [\#715](https://github.com/olivierkes/manuskript/pull/715) ([gedakc](https://github.com/gedakc))
- Remove support for macOS X Sierra \(10.12\) in Travis CI build [\#713](https://github.com/olivierkes/manuskript/pull/713) ([gedakc](https://github.com/gedakc))
- Fixed bugs caused by parallel access during multithreading [\#706](https://github.com/olivierkes/manuskript/pull/706) ([TheJackiMonster](https://github.com/TheJackiMonster))
- More german translations [\#701](https://github.com/olivierkes/manuskript/pull/701) ([fabianbeil](https://github.com/fabianbeil))
- Fixed translation mistake. Trilogy translates to Trilogie in German [\#700](https://github.com/olivierkes/manuskript/pull/700) ([fabianbeil](https://github.com/fabianbeil))
- Fix for Windows 10 Dark Theme on older Qt versions [\#660](https://github.com/olivierkes/manuskript/pull/660) ([worstje](https://github.com/worstje))

## [0.10.0](https://github.com/olivierkes/manuskript/tree/0.10.0) (2019-09-30)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.9.0...0.10.0)

**Implemented enhancements:**

- Add non-enchant spellcheck support [\#505](https://github.com/olivierkes/manuskript/issues/505)
- Basic dark theme support \(Windows 10\) [\#630](https://github.com/olivierkes/manuskript/pull/630) ([worstje](https://github.com/worstje))
- Refactor spellchecker code and add other spellcheck library support [\#507](https://github.com/olivierkes/manuskript/pull/507) ([kakaroto](https://github.com/kakaroto))

**Fixed bugs:**

- Impossible to change UI language to english if your system locale isn't set to an anglophonic country [\#619](https://github.com/olivierkes/manuskript/issues/619)
- All Imports are crashing [\#611](https://github.com/olivierkes/manuskript/issues/611)
- When compiling, it overwrite files without asking [\#608](https://github.com/olivierkes/manuskript/issues/608)
- Crash when exporting with pandoc as custom path only [\#563](https://github.com/olivierkes/manuskript/issues/563)
- Crash on insertion of new page character [\#562](https://github.com/olivierkes/manuskript/issues/562)
- Crash on adding word goal in outline [\#561](https://github.com/olivierkes/manuskript/issues/561)
- Crash in Windows 10 when drag and drop [\#559](https://github.com/olivierkes/manuskript/issues/559)
- Image crash: When using tooltip on an incomplete image filename [\#549](https://github.com/olivierkes/manuskript/issues/549)
- pandoc export crashes if project title is empty [\#535](https://github.com/olivierkes/manuskript/issues/535)
- editor/cork options wrong after deleting a text [\#516](https://github.com/olivierkes/manuskript/issues/516)
-  crash on import directory [\#500](https://github.com/olivierkes/manuskript/issues/500)
- Inconsistent and/or undesirable window placements [\#481](https://github.com/olivierkes/manuskript/issues/481)
- Crash when deleting folder with files in tree view [\#479](https://github.com/olivierkes/manuskript/issues/479)
- New level 'unit' is reset [\#468](https://github.com/olivierkes/manuskript/issues/468)
- Lowering number of saved revisions below 1 crashes program [\#381](https://github.com/olivierkes/manuskript/issues/381)
- ValueError: All strings must be XML compatible: Unicode or ASCII, no NULL bytes or control characters [\#31](https://github.com/olivierkes/manuskript/issues/31)
- OS X: cannot leave fullscreen mode [\#24](https://github.com/olivierkes/manuskript/issues/24)

**Closed issues:**

- Word count goal progress bar broken in develop. [\#652](https://github.com/olivierkes/manuskript/issues/652)
- Fullscreen mode causes spike in CPU [\#643](https://github.com/olivierkes/manuskript/issues/643)
- Italian dictionary [\#638](https://github.com/olivierkes/manuskript/issues/638)
- Manuskript 9.0 crashes when creating new project or opening existing project  [\#631](https://github.com/olivierkes/manuskript/issues/631)
- Spell Check Not working [\#625](https://github.com/olivierkes/manuskript/issues/625)
- story line feature crashing [\#620](https://github.com/olivierkes/manuskript/issues/620)
- Manuskript me fastidio un documento de word [\#616](https://github.com/olivierkes/manuskript/issues/616)
- Feature request: Option to vertically center text input line on screen in fullscreen mode [\#602](https://github.com/olivierkes/manuskript/issues/602)
- Italian translation not applied, application still english. [\#599](https://github.com/olivierkes/manuskript/issues/599)
- File Randomly won't open [\#597](https://github.com/olivierkes/manuskript/issues/597)
- Adding Persian\(Farsi\) in Weblate [\#596](https://github.com/olivierkes/manuskript/issues/596)
- Importing images into Manuskript [\#593](https://github.com/olivierkes/manuskript/issues/593)
- British English translation [\#592](https://github.com/olivierkes/manuskript/issues/592)
- utf-8' codec can't decode byte 0xff in position 0 [\#591](https://github.com/olivierkes/manuskript/issues/591)
- Issue with saving as directory [\#589](https://github.com/olivierkes/manuskript/issues/589)
- Crashes in outliner [\#582](https://github.com/olivierkes/manuskript/issues/582)
- Headings h4 not translated from Markdown to ODF [\#580](https://github.com/olivierkes/manuskript/issues/580)
- \[BUG\] Shim error [\#579](https://github.com/olivierkes/manuskript/issues/579)
- Crash when edit text [\#555](https://github.com/olivierkes/manuskript/issues/555)
- Unusual environment failure [\#547](https://github.com/olivierkes/manuskript/issues/547)
- Won't run \(Arch Linux\) [\#546](https://github.com/olivierkes/manuskript/issues/546)
- Rendre extensible les modèles d'intrigue [\#329](https://github.com/olivierkes/manuskript/issues/329)

**Merged pull requests:**

- Changes to Revisions UI [\#655](https://github.com/olivierkes/manuskript/pull/655) ([worstje](https://github.com/worstje))
- Restore progress bar functionality [\#654](https://github.com/olivierkes/manuskript/pull/654) ([worstje](https://github.com/worstje))
- Default keep revisions to disabled, and remove tests for revisions [\#653](https://github.com/olivierkes/manuskript/pull/653) ([gedakc](https://github.com/gedakc))
- Fix word recognition for spell checker, ignore active partial words [\#651](https://github.com/olivierkes/manuskript/pull/651) ([gedakc](https://github.com/gedakc))
- Fix typo missed in previous commit [\#648](https://github.com/olivierkes/manuskript/pull/648) ([luzpaz](https://github.com/luzpaz))
- Fix source typo [\#645](https://github.com/olivierkes/manuskript/pull/645) ([luzpaz](https://github.com/luzpaz))
- Move Qt 5.11 / 5.12 version warning to Import invocation [\#642](https://github.com/olivierkes/manuskript/pull/642) ([gedakc](https://github.com/gedakc))
- Add DISABLE\_WAYLAND to snapcraft.yaml [\#637](https://github.com/olivierkes/manuskript/pull/637) ([gedakc](https://github.com/gedakc))
- Further refinement of image tooltips \(issue \#593\) [\#629](https://github.com/olivierkes/manuskript/pull/629) ([worstje](https://github.com/worstje))
- Reworking of the translation loading process \(issue \#619\) [\#627](https://github.com/olivierkes/manuskript/pull/627) ([worstje](https://github.com/worstje))
- change markdown to "Markdown" in.... [\#624](https://github.com/olivierkes/manuskript/pull/624) ([leela52452](https://github.com/leela52452))
- Fix tab key order, and default window tab for character & plot panes [\#623](https://github.com/olivierkes/manuskript/pull/623) ([gedakc](https://github.com/gedakc))
- Add British English Translation updates [\#621](https://github.com/olivierkes/manuskript/pull/621) ([gedakc](https://github.com/gedakc))
- Do not prompt "Save project?" when \_Save on quit\_ setting enabled [\#615](https://github.com/olivierkes/manuskript/pull/615) ([gedakc](https://github.com/gedakc))
- Fix exports silently overwriting files \(fixes \#608\) & small fix to dialog logic [\#613](https://github.com/olivierkes/manuskript/pull/613) ([worstje](https://github.com/worstje))
- Working Pandoc import \(fixes \#611\) & small dialog UI update. [\#612](https://github.com/olivierkes/manuskript/pull/612) ([worstje](https://github.com/worstje))
- Fix Linux Travis CI build error - pyenv: version `3.6.3' not installed [\#610](https://github.com/olivierkes/manuskript/pull/610) ([gedakc](https://github.com/gedakc))
- Fix crash when setting word Goal on new Text \(scene\) in Outline pane [\#609](https://github.com/olivierkes/manuskript/pull/609) ([gedakc](https://github.com/gedakc))
- Spelling: Manuscript, could not, process, … No content [\#588](https://github.com/olivierkes/manuskript/pull/588) ([comradekingu](https://github.com/comradekingu))
- fix issue \#468 'unit' is reset [\#587](https://github.com/olivierkes/manuskript/pull/587) ([NocturnalFred](https://github.com/NocturnalFred))
- Fix pandoc export crashes is project title is empty [\#585](https://github.com/olivierkes/manuskript/pull/585) ([gedakc](https://github.com/gedakc))
- Track dirty state and have the UI behave accordingly [\#583](https://github.com/olivierkes/manuskript/pull/583) ([worstje](https://github.com/worstje))
- Fix crash if invalid character is inserted into the text. [\#578](https://github.com/olivierkes/manuskript/pull/578) ([kakaroto](https://github.com/kakaroto))
- Fix crash if using a custom pandoc installation [\#577](https://github.com/olivierkes/manuskript/pull/577) ([kakaroto](https://github.com/kakaroto))
- Fix dialog windows being created outside the desktop area [\#576](https://github.com/olivierkes/manuskript/pull/576) ([kakaroto](https://github.com/kakaroto))
- Fix occasional crashes when \(re\)moving items [\#571](https://github.com/olivierkes/manuskript/pull/571) ([worstje](https://github.com/worstje))
- trying to resolve full screen exit issues on macOS [\#569](https://github.com/olivierkes/manuskript/pull/569) ([dschanoeh](https://github.com/dschanoeh))
- Fix typos in translation format placeholders that lead to crash [\#566](https://github.com/olivierkes/manuskript/pull/566) ([RaphaelWimmer](https://github.com/RaphaelWimmer))
- Fixed \#549 and refactored the image tooltip code [\#558](https://github.com/olivierkes/manuskript/pull/558) ([worstje](https://github.com/worstje))
- Fix typo [\#548](https://github.com/olivierkes/manuskript/pull/548) ([Acid147](https://github.com/Acid147))
- Fix misc. typos [\#489](https://github.com/olivierkes/manuskript/pull/489) ([luzpaz](https://github.com/luzpaz))

## [0.9.0](https://github.com/olivierkes/manuskript/tree/0.9.0) (2019-04-04)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.8.0...0.9.0)

**Implemented enhancements:**

- Add non-enchant spellcheck support [\#505](https://github.com/olivierkes/manuskript/issues/505)
- Fullscreen editor suggestions [\#527](https://github.com/olivierkes/manuskript/issues/527)
- \[Feature Request\] Keyboard shortcuts in Full-Screen mode [\#444](https://github.com/olivierkes/manuskript/issues/444)
- \[Feature Request\] Add Ability to Add Image When Creating Fullscreen Theme [\#399](https://github.com/olivierkes/manuskript/issues/399)
- Making Fullscreen Mode Great Again [\#234](https://github.com/olivierkes/manuskript/issues/234)

**Fixed bugs:**

- Crash when previewing malformed regular expression when compiling [\#488](https://github.com/olivierkes/manuskript/issues/488)
- Spellcheck On/Off setting ignored / Manuskript unresponsive [\#474](https://github.com/olivierkes/manuskript/issues/474)
- Wrong codepage for import causes crash [\#470](https://github.com/olivierkes/manuskript/issues/470)
- Full-screen mode right-click menu black text on black background [\#440](https://github.com/olivierkes/manuskript/issues/440)
- Application language still the same after changing it in the settings. [\#411](https://github.com/olivierkes/manuskript/issues/411)

**Closed issues:**

- Python issues? lxml [\#541](https://github.com/olivierkes/manuskript/issues/541)
- Cannot open a project. [\#529](https://github.com/olivierkes/manuskript/issues/529)
- Corrupted Project File Crashes When Opening.  [\#522](https://github.com/olivierkes/manuskript/issues/522)
- Specific document suddenly won't open [\#502](https://github.com/olivierkes/manuskript/issues/502)
- trying to get pandoc to work manuskript 0.8.0 Win10 64 [\#475](https://github.com/olivierkes/manuskript/issues/475)
- Editor does not show text [\#472](https://github.com/olivierkes/manuskript/issues/472)
- Application crashes when trying to save "…" [\#461](https://github.com/olivierkes/manuskript/issues/461)
- Feature Request: script writing interface for manuskript  [\#435](https://github.com/olivierkes/manuskript/issues/435)
- suggestion: Use sudo for your Fedora install instructions, not su -c [\#573](https://github.com/olivierkes/manuskript/issues/573)
- Chinese translation filename suffix [\#428](https://github.com/olivierkes/manuskript/issues/428)

**Merged pull requests:**

- Fix color scheme of fullscreen editor [\#539](https://github.com/olivierkes/manuskript/pull/539) ([kakaroto](https://github.com/kakaroto))
- Directory entries in ZIP break loading code [\#531](https://github.com/olivierkes/manuskript/pull/531) ([worstje](https://github.com/worstje))
- Providing a suitable icon for consumption by Windows operating systems [\#530](https://github.com/olivierkes/manuskript/pull/530) ([worstje](https://github.com/worstje))
- Ensure text file open methods use utf-8 encoding [\#515](https://github.com/olivierkes/manuskript/pull/515) ([gedakc](https://github.com/gedakc))
- Fix crash when right-clicking twice on fullscreen panel in Windows 10 [\#514](https://github.com/olivierkes/manuskript/pull/514) ([kakaroto](https://github.com/kakaroto))
- Add support for IPython Jupyter QT Console as a debugging aid [\#513](https://github.com/olivierkes/manuskript/pull/513) ([kakaroto](https://github.com/kakaroto))
- Fix background of popup menus that were transparent \(black\) [\#512](https://github.com/olivierkes/manuskript/pull/512) ([kakaroto](https://github.com/kakaroto))
- Add snap build and package [\#511](https://github.com/olivierkes/manuskript/pull/511) ([tomwardill](https://github.com/tomwardill))
- Add ability to add new background images through UI. [\#510](https://github.com/olivierkes/manuskript/pull/510) ([kakaroto](https://github.com/kakaroto))
- Fullscreen panels improvements [\#509](https://github.com/olivierkes/manuskript/pull/509) ([kakaroto](https://github.com/kakaroto))
- Fix corkView background image on Windows [\#508](https://github.com/olivierkes/manuskript/pull/508) ([kakaroto](https://github.com/kakaroto))
- Do not default spellcheck to True for new editor views [\#506](https://github.com/olivierkes/manuskript/pull/506) ([kakaroto](https://github.com/kakaroto))
- Set editor theme stylesheet to QTextEdit only. [\#504](https://github.com/olivierkes/manuskript/pull/504) ([kakaroto](https://github.com/kakaroto))
- Fix fullscreen editor's myScrollBar delayed destruction causing a crash [\#503](https://github.com/olivierkes/manuskript/pull/503) ([kakaroto](https://github.com/kakaroto))
- 2nd try to fix macOS X blank screen when leaving fullscreen editor mode [\#495](https://github.com/olivierkes/manuskript/pull/495) ([gedakc](https://github.com/gedakc))
- Fix crash when right clicking a word in editor and enchant is not installed [\#492](https://github.com/olivierkes/manuskript/pull/492) ([kakaroto](https://github.com/kakaroto))
- Don't crash if a typo is made in the exporter's regular expression. [\#486](https://github.com/olivierkes/manuskript/pull/486) ([kakaroto](https://github.com/kakaroto))
- Fix crash when previewing pandoc HTML with QTextEdit as web renderer… [\#485](https://github.com/olivierkes/manuskript/pull/485) ([kakaroto](https://github.com/kakaroto))
- Fix crash when 7 pound signs are written alone on a line. [\#484](https://github.com/olivierkes/manuskript/pull/484) ([kakaroto](https://github.com/kakaroto))
- Try to fix macOS X blank screen when leaving editor fullscreen mode [\#482](https://github.com/olivierkes/manuskript/pull/482) ([gedakc](https://github.com/gedakc))
- Fix wrong codepage crash on import with Windows 10 [\#478](https://github.com/olivierkes/manuskript/pull/478) ([gedakc](https://github.com/gedakc))
- Spelling: Manuscript, may have to be restarted [\#454](https://github.com/olivierkes/manuskript/pull/454) ([comradekingu](https://github.com/comradekingu))
- Chinese translation [\#434](https://github.com/olivierkes/manuskript/pull/434) ([lingsamuel](https://github.com/lingsamuel))
- fix translator [\#433](https://github.com/olivierkes/manuskript/pull/433) ([lingsamuel](https://github.com/lingsamuel))
- Remember last accessed directory [\#431](https://github.com/olivierkes/manuskript/pull/431) ([lingsamuel](https://github.com/lingsamuel))
- translation suffix, change translation load order [\#430](https://github.com/olivierkes/manuskript/pull/430) ([lingsamuel](https://github.com/lingsamuel))

## [0.8.0](https://github.com/olivierkes/manuskript/tree/0.8.0) (2018-12-05)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.7.0...0.8.0)

**Fixed bugs:**

- Snowflake Method option is greyed out. [\#419](https://github.com/olivierkes/manuskript/issues/419)
- Plots bounce around main, secondary, and minor -- unsatisfactory solution? [\#404](https://github.com/olivierkes/manuskript/issues/404)
- Segmentation fault on import [\#402](https://github.com/olivierkes/manuskript/issues/402)
- "Corrupted" settings and impossibility to start [\#377](https://github.com/olivierkes/manuskript/issues/377)
- Resolution step deleting itself on pressing Ctrl + Backspace [\#375](https://github.com/olivierkes/manuskript/issues/375)
- Develop Branch Crashes in Outline View [\#355](https://github.com/olivierkes/manuskript/issues/355)
- Export crashes, because of encoding to 1250 [\#331](https://github.com/olivierkes/manuskript/issues/331)
- pandoc v2 has deprecated some options and extensions so manuskript is giving error. [\#304](https://github.com/olivierkes/manuskript/issues/304)
- Compile Issue for Pandoc Formats - pandoc.exe incorrect [\#186](https://github.com/olivierkes/manuskript/issues/186)

**Closed issues:**

- Problems with running from 0.7.0 pyinstaller package on mac os x 10.13 [\#386](https://github.com/olivierkes/manuskript/issues/386)
- Old bugs in current version 0.6.0 \(with crosslinks and details\) [\#371](https://github.com/olivierkes/manuskript/issues/371)
- pt\_PT translation and Weblate [\#408](https://github.com/olivierkes/manuskript/issues/408)
- Italian translation [\#395](https://github.com/olivierkes/manuskript/issues/395)
- Snowflake view mode always disabled [\#45](https://github.com/olivierkes/manuskript/issues/45)

**Merged pull requests:**

- Remove unimplemented snowflake view mode menu entry [\#424](https://github.com/olivierkes/manuskript/pull/424) ([gedakc](https://github.com/gedakc))
- Increase Travis CI macOS X build minimum to Sierra \(10.12\) [\#423](https://github.com/olivierkes/manuskript/pull/423) ([gedakc](https://github.com/gedakc))
- Remove plot resolution step key bindings Ctrl+Enter and Ctrl+Backspace [\#420](https://github.com/olivierkes/manuskript/pull/420) ([gedakc](https://github.com/gedakc))
- Add support for pandoc version 2 [\#418](https://github.com/olivierkes/manuskript/pull/418) ([gedakc](https://github.com/gedakc))
- Prevent build and deploy steps for linux on Travis CI [\#414](https://github.com/olivierkes/manuskript/pull/414) ([gedakc](https://github.com/gedakc))
- Limit pyinstaller package build and deploy to osx on Travis CI [\#413](https://github.com/olivierkes/manuskript/pull/413) ([gedakc](https://github.com/gedakc))
- Fix segmentation fault on import [\#412](https://github.com/olivierkes/manuskript/pull/412) ([gedakc](https://github.com/gedakc))
- Fix pytest warnings [\#407](https://github.com/olivierkes/manuskript/pull/407) ([gedakc](https://github.com/gedakc))
- Fix plot importance changes if delete earlier plot and click other plots [\#406](https://github.com/olivierkes/manuskript/pull/406) ([gedakc](https://github.com/gedakc))
- Enable testing in TravisCI [\#403](https://github.com/olivierkes/manuskript/pull/403) ([katafrakt](https://github.com/katafrakt))
- Fix Travis CI build for Mac OSX - pip3: command not found [\#400](https://github.com/olivierkes/manuskript/pull/400) ([gedakc](https://github.com/gedakc))
- Moved incorrectly placed parameter to correct place. Closes \#377. [\#389](https://github.com/olivierkes/manuskript/pull/389) ([RiderExMachina](https://github.com/RiderExMachina))

## [0.7.0](https://github.com/olivierkes/manuskript/tree/0.7.0) (2018-08-15)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.6.0...0.7.0)

**Implemented enhancements:**

- Display images as tooltip [\#270](https://github.com/olivierkes/manuskript/issues/270)
- Focus mode [\#259](https://github.com/olivierkes/manuskript/issues/259)
- Add markdown support of other tabs [\#232](https://github.com/olivierkes/manuskript/issues/232)
- Translation automation [\#228](https://github.com/olivierkes/manuskript/issues/228)
- Add: command line parameter to open project [\#223](https://github.com/olivierkes/manuskript/issues/223)
- Moving World Items [\#219](https://github.com/olivierkes/manuskript/issues/219)
- Make http links clickable in markdown editor [\#215](https://github.com/olivierkes/manuskript/issues/215)
- Feature suggestion: Typewriter scrolling. [\#175](https://github.com/olivierkes/manuskript/issues/175)
- Request for Bullets and Numbering option [\#123](https://github.com/olivierkes/manuskript/issues/123)
- Markdown syntax highlighting [\#13](https://github.com/olivierkes/manuskript/issues/13)
- Add moving World Items [\#298](https://github.com/olivierkes/manuskript/pull/298) ([JackXVII](https://github.com/JackXVII))

**Fixed bugs:**

- Install on MacOsX failed [\#282](https://github.com/olivierkes/manuskript/issues/282)
- Crash if Cheatsheet filter term not found and Enter key pressed [\#354](https://github.com/olivierkes/manuskript/issues/354)
- Overlay status bar prevents access to add/delete world item icons when displaying a message [\#307](https://github.com/olivierkes/manuskript/issues/307)
- Deleting multiple World items leaves/creates two empty items [\#306](https://github.com/olivierkes/manuskript/issues/306)
- Underline causes false spelling error [\#283](https://github.com/olivierkes/manuskript/issues/283)
- .DS\_Store files let crash Manuskript when opening project [\#281](https://github.com/olivierkes/manuskript/issues/281)
- Programm killed by Hovereffekt? [\#275](https://github.com/olivierkes/manuskript/issues/275)
- Spell check is crashing the program [\#273](https://github.com/olivierkes/manuskript/issues/273)
- Highlight Contrast Problem [\#272](https://github.com/olivierkes/manuskript/issues/272)
- Segfault when pasting text with focus mode enabled [\#271](https://github.com/olivierkes/manuskript/issues/271)
- Compile Check Box not working in Outline view [\#263](https://github.com/olivierkes/manuskript/issues/263)
- Manuskript response slow with recent addition of focus mode [\#261](https://github.com/olivierkes/manuskript/issues/261)
- Organize Menu is not disabled on startup [\#260](https://github.com/olivierkes/manuskript/issues/260)
- Ctrl+tab gets trapped in Debug tab [\#249](https://github.com/olivierkes/manuskript/issues/249)
- Index card status can spillover [\#246](https://github.com/olivierkes/manuskript/issues/246)
- Cannot write a summary on a plot resolution step [\#240](https://github.com/olivierkes/manuskript/issues/240)
- Format buttons in text editor window not working [\#59](https://github.com/olivierkes/manuskript/issues/59)
- stop crash when click btnGoUp and current editor is None [\#318](https://github.com/olivierkes/manuskript/pull/318) ([Windspar](https://github.com/Windspar))
- Avoid crash on spellcheck by ensuring enchant dictionary exists [\#303](https://github.com/olivierkes/manuskript/pull/303) ([gedakc](https://github.com/gedakc))
- Skip loading directory and file names that begin with a period [\#302](https://github.com/olivierkes/manuskript/pull/302) ([gedakc](https://github.com/gedakc))

**Closed issues:**

- \[Feature request\] Russian translation [\#358](https://github.com/olivierkes/manuskript/issues/358)
- Manuskript crashes during save process and "corrupts" the msk-file [\#352](https://github.com/olivierkes/manuskript/issues/352)
- Add polish translation  [\#289](https://github.com/olivierkes/manuskript/issues/289)
- \[Feature request\] Accept first command line argument as project file name to open [\#278](https://github.com/olivierkes/manuskript/issues/278)
- Status bar distracting when saving with current develop branch [\#262](https://github.com/olivierkes/manuskript/issues/262)
- Editor Consistency [\#257](https://github.com/olivierkes/manuskript/issues/257)
- French Tab in English Mode [\#253](https://github.com/olivierkes/manuskript/issues/253)
- I want to translate it to portuguese [\#230](https://github.com/olivierkes/manuskript/issues/230)

**Merged pull requests:**

- Fix Travix CI build error on OSX installing python3 [\#338](https://github.com/olivierkes/manuskript/pull/338) ([gedakc](https://github.com/gedakc))
- Use QPersistentModelIndex in textEditView [\#308](https://github.com/olivierkes/manuskript/pull/308) ([JackXVII](https://github.com/JackXVII))
- Add automated script to create RPM package [\#368](https://github.com/olivierkes/manuskript/pull/368) ([gedakc](https://github.com/gedakc))
- Build MacOS release with XCode 7.3 image [\#287](https://github.com/olivierkes/manuskript/pull/287) ([katafrakt](https://github.com/katafrakt))

## [0.6.0](https://github.com/olivierkes/manuskript/tree/0.6.0) (2017-11-29)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.5.0...0.6.0)

**Implemented enhancements:**

- Adds: document menu \(copy, paste, delete, duplicate, split, merge, etc.\) [\#229](https://github.com/olivierkes/manuskript/issues/229)
- Add transparent text editor [\#216](https://github.com/olivierkes/manuskript/issues/216)
- Add Mind Map Import [\#208](https://github.com/olivierkes/manuskript/issues/208)
- Adds: Importer \(docx, html, opml, …\) [\#200](https://github.com/olivierkes/manuskript/issues/200)
- Add a "Rename Item" option to context menu in the Tree view [\#189](https://github.com/olivierkes/manuskript/issues/189)
- Pandoc output: add more custom settings [\#173](https://github.com/olivierkes/manuskript/issues/173)

**Fixed bugs:**

- Manuskript fails to run in Ubuntu 14.04 [\#225](https://github.com/olivierkes/manuskript/issues/225)
- Program Crash on Import with images [\#213](https://github.com/olivierkes/manuskript/issues/213)
- Missing default file extension when Saving As... [\#211](https://github.com/olivierkes/manuskript/issues/211)
- One white pixel visible in full screen mode [\#210](https://github.com/olivierkes/manuskript/issues/210)
- Accentueted characters on linux [\#207](https://github.com/olivierkes/manuskript/issues/207)
- Manuskript crashes when creating new document on Ubuntu [\#198](https://github.com/olivierkes/manuskript/issues/198)
- Editor tab should trim long titles [\#194](https://github.com/olivierkes/manuskript/issues/194)
- Manuskript does not start with PyEnchant on MacOS [\#188](https://github.com/olivierkes/manuskript/issues/188)
- Index card text almost invisible in dark themes. [\#183](https://github.com/olivierkes/manuskript/issues/183)
- Accented characters not working [\#141](https://github.com/olivierkes/manuskript/issues/141)
- Accent not working [\#105](https://github.com/olivierkes/manuskript/issues/105)
- Accent marks not working [\#58](https://github.com/olivierkes/manuskript/issues/58)

**Closed issues:**

- new dalolog icon [\#237](https://github.com/olivierkes/manuskript/issues/237)
- Cannot select folder on create new project [\#224](https://github.com/olivierkes/manuskript/issues/224)
- Should pandoc be bundled with manuskript's packages? [\#190](https://github.com/olivierkes/manuskript/issues/190)
- Odd word choices in English - Take 2 [\#181](https://github.com/olivierkes/manuskript/issues/181)

**Merged pull requests:**

- Change words issue 181 [\#231](https://github.com/olivierkes/manuskript/pull/231) ([gedakc](https://github.com/gedakc))
- Add PyEnchant support to OSX builds [\#212](https://github.com/olivierkes/manuskript/pull/212) ([katafrakt](https://github.com/katafrakt))
- Update README.md for 0.5.0 release [\#205](https://github.com/olivierkes/manuskript/pull/205) ([gedakc](https://github.com/gedakc))
- \[WIP\] Add Travis CI support [\#203](https://github.com/olivierkes/manuskript/pull/203) ([katafrakt](https://github.com/katafrakt))
- Get default enchant Dict language in more reliable way [\#202](https://github.com/olivierkes/manuskript/pull/202) ([katafrakt](https://github.com/katafrakt))
- Expand german translation [\#193](https://github.com/olivierkes/manuskript/pull/193) ([ScullyBlue](https://github.com/ScullyBlue))
- Adds: Import OPML [\#192](https://github.com/olivierkes/manuskript/pull/192) ([camstevenson](https://github.com/camstevenson))

## [0.5.0](https://github.com/olivierkes/manuskript/tree/0.5.0) (2017-10-31)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.4.0...0.5.0)

**Implemented enhancements:**

- Swedish translation \(sv-SE\). [\#177](https://github.com/olivierkes/manuskript/issues/177)
- Spanish transalation for manuskript 0.5.0 [\#174](https://github.com/olivierkes/manuskript/issues/174)
- Suggestion: Configurable editor margins. [\#168](https://github.com/olivierkes/manuskript/issues/168)
- Feature request: disable cursor blinking [\#165](https://github.com/olivierkes/manuskript/issues/165)
- Suggestion: Block insertion cursor. [\#163](https://github.com/olivierkes/manuskript/issues/163)
- New navigation icon design [\#159](https://github.com/olivierkes/manuskript/issues/159)
- New flash card design [\#158](https://github.com/olivierkes/manuskript/issues/158)
- Redaction view navigation improvements [\#157](https://github.com/olivierkes/manuskript/issues/157)
- Request: Justified formatting of text [\#148](https://github.com/olivierkes/manuskript/issues/148)
- Ability to always show word target in distraction free mode [\#109](https://github.com/olivierkes/manuskript/issues/109)
- Use on smaller resolution screens [\#108](https://github.com/olivierkes/manuskript/issues/108)
- Odd wordchoices in English. [\#53](https://github.com/olivierkes/manuskript/issues/53)

**Fixed bugs:**

- Bug in 'World' section [\#126](https://github.com/olivierkes/manuskript/issues/126)
- Redaction's tab problem in 0.3.0 win version [\#92](https://github.com/olivierkes/manuskript/issues/92)
- Application Style setting GTK+ on Linux Mint Mate  [\#57](https://github.com/olivierkes/manuskript/issues/57)
- Likes to freeze and crash [\#50](https://github.com/olivierkes/manuskript/issues/50)
- Seg faults found [\#9](https://github.com/olivierkes/manuskript/issues/9)
- Installation - Qt platforn plugin "xcb" not found [\#8](https://github.com/olivierkes/manuskript/issues/8)
- Untranslatable strings. [\#178](https://github.com/olivierkes/manuskript/issues/178)
- Create new project ignores changes made to template levels before Create [\#171](https://github.com/olivierkes/manuskript/issues/171)
- Several bugs in drag'n'dropping items [\#169](https://github.com/olivierkes/manuskript/issues/169)
- Some panels require initial two clicks of RHS tab to hide [\#167](https://github.com/olivierkes/manuskript/issues/167)
- Spell checker is active for partial words. [\#166](https://github.com/olivierkes/manuskript/issues/166)
- Spell checking works but does not underline misspelled words [\#147](https://github.com/olivierkes/manuskript/issues/147)
- Contrast Problem in Notes/Refences with Dark Background [\#143](https://github.com/olivierkes/manuskript/issues/143)
- Crash when permissions don't allow saving [\#138](https://github.com/olivierkes/manuskript/issues/138)
- App crash when moving a step in Plots section [\#134](https://github.com/olivierkes/manuskript/issues/134)
- Indent not saved in custom full screen theme [\#133](https://github.com/olivierkes/manuskript/issues/133)
- 'Save as' only partly works [\#128](https://github.com/olivierkes/manuskript/issues/128)
- "pandoc: Could not parse YAML header" error [\#124](https://github.com/olivierkes/manuskript/issues/124)
- Distraction free mode crashes with time target [\#119](https://github.com/olivierkes/manuskript/issues/119)
- Pandoc PDF output error with unicode characters [\#117](https://github.com/olivierkes/manuskript/issues/117)
- Character Importance-Slider memorize importance of last character ... partly [\#102](https://github.com/olivierkes/manuskript/issues/102)
- Index cards seem to keep a background image by default. [\#52](https://github.com/olivierkes/manuskript/issues/52)
- In revision mode text, selecting group doesn't load text-preferences right. [\#51](https://github.com/olivierkes/manuskript/issues/51)
- Undo/redo works in some text areas but not others [\#34](https://github.com/olivierkes/manuskript/issues/34)
- Some bugs in Windows XP and Ubuntu 15.1 [\#25](https://github.com/olivierkes/manuskript/issues/25)
- Stylesheet error on windows [\#18](https://github.com/olivierkes/manuskript/issues/18)
- Manuskript fails to load last state of panels [\#14](https://github.com/olivierkes/manuskript/issues/14)
- Multiple selections of items sometimes gets Notes/references field to be ereased [\#10](https://github.com/olivierkes/manuskript/issues/10)

**Closed issues:**

- Cannot start manuskript due to import error [\#179](https://github.com/olivierkes/manuskript/issues/179)
- Does not run on Ubuntu 17.10 [\#170](https://github.com/olivierkes/manuskript/issues/170)
- Add translation with transifex.com [\#140](https://github.com/olivierkes/manuskript/issues/140)
- Site of Manuskript is not in the air at the moment [\#139](https://github.com/olivierkes/manuskript/issues/139)
- Manuskript Fail to Launch After Several Successes on Windows 10 [\#132](https://github.com/olivierkes/manuskript/issues/132)
- Index Card Background Freeze [\#127](https://github.com/olivierkes/manuskript/issues/127)
- Keyboard shortcuts aren't functioning, No undo feature.   [\#125](https://github.com/olivierkes/manuskript/issues/125)
- Trojan in current windows installer? [\#112](https://github.com/olivierkes/manuskript/issues/112)
- Manuskript no longer opening [\#106](https://github.com/olivierkes/manuskript/issues/106)
- not working on Mac [\#35](https://github.com/olivierkes/manuskript/issues/35)

**Merged pull requests:**

- Change message from warning to note for failed to load translator string [\#110](https://github.com/olivierkes/manuskript/pull/110) ([gedakc](https://github.com/gedakc))
- Add about manuskript dialog [\#153](https://github.com/olivierkes/manuskript/pull/153) ([gedakc](https://github.com/gedakc))
- Add help tip for world tab [\#151](https://github.com/olivierkes/manuskript/pull/151) ([gedakc](https://github.com/gedakc))
- Add missing \_\_init\_\_.py file [\#149](https://github.com/olivierkes/manuskript/pull/149) ([gedakc](https://github.com/gedakc))
- Fixes: Manuskript fails to load last state of panels [\#136](https://github.com/olivierkes/manuskript/pull/136) ([gedakc](https://github.com/gedakc))
- Add to README a HowTo section with link to Wiki [\#131](https://github.com/olivierkes/manuskript/pull/131) ([gedakc](https://github.com/gedakc))
- Fixes: Contents missing when non-single file project saved with Save as [\#129](https://github.com/olivierkes/manuskript/pull/129) ([gedakc](https://github.com/gedakc))
- Fixes: add character button does not set importance slider to default… [\#121](https://github.com/olivierkes/manuskript/pull/121) ([gedakc](https://github.com/gedakc))
- Request confirmation if create project would overwrite existing file\(s\) [\#114](https://github.com/olivierkes/manuskript/pull/114) ([gedakc](https://github.com/gedakc))
- Fixes: Unable to change index cards background from image to a color [\#113](https://github.com/olivierkes/manuskript/pull/113) ([gedakc](https://github.com/gedakc))
- Add project name to main window title [\#103](https://github.com/olivierkes/manuskript/pull/103) ([gedakc](https://github.com/gedakc))
- Fixes: after project close, open or create project fails [\#100](https://github.com/olivierkes/manuskript/pull/100) ([gedakc](https://github.com/gedakc))
- Fixes: incorrect reference to 32px icon [\#97](https://github.com/olivierkes/manuskript/pull/97) ([gedakc](https://github.com/gedakc))

## [0.4.0](https://github.com/olivierkes/manuskript/tree/0.4.0) (2017-05-25)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.3.0...0.4.0)

**Implemented enhancements:**

- Export into text? \[feature suggestion\] [\#80](https://github.com/olivierkes/manuskript/issues/80)
- Default background for fullscreen mode is unusable \[minor\] [\#79](https://github.com/olivierkes/manuskript/issues/79)
- Documention Needed [\#69](https://github.com/olivierkes/manuskript/issues/69)
- Compile dialog issues: cancel doesn't seem to do anything, default ouput directory wrong [\#77](https://github.com/olivierkes/manuskript/issues/77)
- OS X app with Platypus [\#28](https://github.com/olivierkes/manuskript/issues/28)

**Fixed bugs:**

- Unable to type the "ê" character [\#46](https://github.com/olivierkes/manuskript/issues/46)
- Bug: File doesn't open if spellcheck is active and dictionary is missing [\#26](https://github.com/olivierkes/manuskript/issues/26)
- Installed PyEnchant but Manuskript still asks me to "Install PyEnchant to use Spellcheck" [\#122](https://github.com/olivierkes/manuskript/issues/122)
- Crashes when trying to create or open the project [\#99](https://github.com/olivierkes/manuskript/issues/99)
- After close project, open or create project fails [\#96](https://github.com/olivierkes/manuskript/issues/96)
- Crash on create - Linux Mint 18 [\#91](https://github.com/olivierkes/manuskript/issues/91)
- Compile not honoring check marks [\#90](https://github.com/olivierkes/manuskript/issues/90)
- Plots, resolutions steps screen: columns not sizeable. [\#87](https://github.com/olivierkes/manuskript/issues/87)
- word count [\#72](https://github.com/olivierkes/manuskript/issues/72)
- Cant create a new project using Ubuntu 16.10 [\#70](https://github.com/olivierkes/manuskript/issues/70)
- Fails to create a project in Linux [\#65](https://github.com/olivierkes/manuskript/issues/65)
- does not compile to OpenOffice format [\#61](https://github.com/olivierkes/manuskript/issues/61)
- Doesn't save in redaction [\#55](https://github.com/olivierkes/manuskript/issues/55)
- Error "Fail to load translator..." [\#49](https://github.com/olivierkes/manuskript/issues/49)
- Crash at project creation on mac [\#48](https://github.com/olivierkes/manuskript/issues/48)
- crash on create new project [\#44](https://github.com/olivierkes/manuskript/issues/44)
- epiphany section in basic infos for characters not saved [\#43](https://github.com/olivierkes/manuskript/issues/43)
- 0.3.0 File Creation Issues [\#37](https://github.com/olivierkes/manuskript/issues/37)
- Can't create new project on Linux [\#30](https://github.com/olivierkes/manuskript/issues/30)
- Problem with minimum size of program window? [\#29](https://github.com/olivierkes/manuskript/issues/29)
- Bug: Writing a .msk file in linux and opening it in windows clean the outline files [\#27](https://github.com/olivierkes/manuskript/issues/27)
- Welcome windows on OS X: single click instead of double click [\#23](https://github.com/olivierkes/manuskript/issues/23)
- AttributeError in editorWidget [\#11](https://github.com/olivierkes/manuskript/issues/11)

**Closed issues:**

- File creation fails and causes Manuskript to crash [\#93](https://github.com/olivierkes/manuskript/issues/93)
- Failed to load translator [\#89](https://github.com/olivierkes/manuskript/issues/89)
- crashing on initial save \(again?\) [\#88](https://github.com/olivierkes/manuskript/issues/88)
- Impossible to start a project on Lubuntu 16.04 [\#85](https://github.com/olivierkes/manuskript/issues/85)
- Manuskript 0.3.0 crash on Windows 10 [\#83](https://github.com/olivierkes/manuskript/issues/83)
- on Fedora 25 Manuskript doesn't start [\#82](https://github.com/olivierkes/manuskript/issues/82)
- \(l\)ubuntu dependencies for develop branch [\#81](https://github.com/olivierkes/manuskript/issues/81)
- Creating new project fails [\#76](https://github.com/olivierkes/manuskript/issues/76)
- Missing module when launching from github \[Xubuntu 16.04.1 LTS\] [\#73](https://github.com/olivierkes/manuskript/issues/73)
- Download does not run on 32bit Linux [\#63](https://github.com/olivierkes/manuskript/issues/63)
- Locale Warning [\#62](https://github.com/olivierkes/manuskript/issues/62)
- Crashes when creating new project [\#60](https://github.com/olivierkes/manuskript/issues/60)
- Is This An Active Project [\#56](https://github.com/olivierkes/manuskript/issues/56)
- Qt WebKit is deprecated [\#54](https://github.com/olivierkes/manuskript/issues/54)
- Unable to run application [\#47](https://github.com/olivierkes/manuskript/issues/47)
- \[Windows\] Compile Dialog does not have a title [\#39](https://github.com/olivierkes/manuskript/issues/39)
- Creating manuskript binay for Android and IOS [\#21](https://github.com/olivierkes/manuskript/issues/21)
- Compiling Manuskript in windows [\#19](https://github.com/olivierkes/manuskript/issues/19)
- No distance between two scenes in compiled document [\#104](https://github.com/olivierkes/manuskript/issues/104)
- Small typographic error in the README [\#84](https://github.com/olivierkes/manuskript/issues/84)
- \[Windows\] HTML compiled file title is "FIXME" [\#42](https://github.com/olivierkes/manuskript/issues/42)
- \[Windows\] Compile operation does not adds the file extension when the file type option is changed [\#41](https://github.com/olivierkes/manuskript/issues/41)
- \[Windows\] Compile dialog comes with development machine default location [\#40](https://github.com/olivierkes/manuskript/issues/40)
- \[Windows\] Cancel Button on Compile Dialog does not work [\#38](https://github.com/olivierkes/manuskript/issues/38)

**Merged pull requests:**

- Fixes: field "Source of conflict" in World is not active [\#95](https://github.com/olivierkes/manuskript/pull/95) ([gedakc](https://github.com/gedakc))
- Fixes: epiphany section in basic infos for characters not saved \#43 [\#94](https://github.com/olivierkes/manuskript/pull/94) ([gedakc](https://github.com/gedakc))
- Updating README.md [\#68](https://github.com/olivierkes/manuskript/pull/68) ([olivierkes](https://github.com/olivierkes))
- added commands to install dependencies to README [\#67](https://github.com/olivierkes/manuskript/pull/67) ([wmww](https://github.com/wmww))
- Added spanish translation \(and changed "chuleta" for "guía rápida"\). [\#66](https://github.com/olivierkes/manuskript/pull/66) ([jmgaguilera](https://github.com/jmgaguilera))

## [0.3.0](https://github.com/olivierkes/manuskript/tree/0.3.0) (2016-03-31)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.2.0...0.3.0)

**Fixed bugs:**

- Windows package fails antivirus scan [\#15](https://github.com/olivierkes/manuskript/issues/15)
- DictNotFoundError when dict language specified in settings is not installed [\#12](https://github.com/olivierkes/manuskript/issues/12)
- Manuskript fails to lauch on Windows [\#7](https://github.com/olivierkes/manuskript/issues/7)
- The plot line colours keep changing? [\#6](https://github.com/olivierkes/manuskript/issues/6)

**Closed issues:**

- Windows installation issue [\#16](https://github.com/olivierkes/manuskript/issues/16)

## [0.2.0](https://github.com/olivierkes/manuskript/tree/0.2.0) (2016-02-28)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.1.1...0.2.0)

**Fixed bugs:**

- Fullscreen editor error when text is empty \(wordcount = 0\) [\#3](https://github.com/olivierkes/manuskript/issues/3)
- Save file doesn't automatically add .msk [\#2](https://github.com/olivierkes/manuskript/issues/2)

## [0.1.1](https://github.com/olivierkes/manuskript/tree/0.1.1) (2016-02-08)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/0.1.0...0.1.1)

**Fixed bugs:**

- Crash on initial save [\#1](https://github.com/olivierkes/manuskript/issues/1)

## [0.1.0](https://github.com/olivierkes/manuskript/tree/0.1.0) (2016-02-06)

[Full Changelog](https://github.com/olivierkes/manuskript/compare/5df82d5e2de7cadd75b013c48ce4575688dd804a...0.1.0)



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
