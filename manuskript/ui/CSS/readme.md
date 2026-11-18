The following are available colors

```window for General background
windowText for General foreground
base for Other background
alternateBase = for alternative Other background
text for Base Text
brightText for Contrast Text
button for Button background
buttonText for Button Text
highlight for Other background
highlightedText for Base highlighted Text
link for Links
linkVisited for visited Links
light for color Lighter than Button color
midlight for color Between Button and Light
mid for color Between Button and Dark
dark for color Darker than Button
shadow for a very dark color
highlightLight for a light Other background/mix between highlight and window
highlightedTextDark for dark highlighted Text/mix between highlight and text
highlightedTextLight for light highlighted Text/mix between highlight and highlightedText
midlighter = mixColors(mid, window, .4)
textLight = mixColors(window, text)
textLighter = mixColors(window, text, .85)
```

Note, css must begin on new lines, and all include files must be in this directory and have a .css extenstion

```css
/* will work */
QScrollBar::handle {
    background: {handle};
} 
/* will fail because the { wont be formated properly */
QScrollBar::handle {background: {handle};}
```
