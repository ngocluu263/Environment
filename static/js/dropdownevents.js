/*=======================================================================*\
|  @class DropDownEvents(spanid,txtid,selid,butid)
|  @brief A class that supports drop down editable text fields.
| 
|  A class that handles event related operations for text fields
|  with drop down boxes of possible options.  Note, the text field
|  allows arbitrary editing, while the drop down box provides 
|  suggested entries for the text field.
| 
|  @param spanid The docid for the span that encloses the drop down.
|  @param txtid The docid for the text field.
|  @param selid The docid for the select field.
|  @param butid The docid for the drop down arrow button.
|  @return None.
\*======================================================================*/
function DropDownEvents(spanid,txtid,selid,butid) {
  this.is_open = false;  // true when the drop down selection is open
  this.my_docspan = document.getElementById(spanid); // docid for the span
  this.my_doctxt = document.getElementById(txtid); // docid for the text field
  this.my_docsel = document.getElementById(selid); // docid for the select
  this.my_docbut = document.getElementById(butid); // docid for the button
  this.my_doctxt_border = this.my_doctxt.style.borderColor;
  this.enabled = true;

  // -----------------------------------------------------------------------
  // @fn enableButton()
  // @brief Enable the drop down box button.
  //
  // Enable the drop down box button.  Enables and
  // un-greys the selection arrow.
  //
  // @return None.
  //
  this.enableButton = function() {
    //this.my_docbut.src = 'images/dropboxarrow.png';
    this.my_docbut.disabled = false;
  }

  // -----------------------------------------------------------------------
  // @fn disableButton()
  // @brief Disable the drop down box button.
  //
  // Disable the drop down box button.  Disables and
  // greys the selection arrow.
  //
  // @return None.
  //
  this.disableButton = function() {
    //this.my_docbut.src = 'images/dropboxarrow-grey.png';
    this.my_docbut.disabled = true;
  }

  // -----------------------------------------------------------------------
  // @fn enable(val)
  // @brief Enable the drop down box for data entry.
  //
  // Enable the drop down box for data entry.  Both enables the
  // form elements and un-greys the selection arrow.  If val is null
  // the element value will not be changed.
  //
  // @param val The default value for enabled text field or null.
  // @return None.
  //
  this.enable = function(val) {
    if (val != null) this.my_doctxt.value = val;
    this.my_doctxt.disabled = false;
    //this.my_doctxt.style.borderColor = "black black black black";
    console.log("set border color");
    this.enableButton();
    this.my_doctxt.style.borderColor = this.my_doctxt.border;
    this.enabled = true;
  }

  // -----------------------------------------------------------------------
  // @fn disable(keepval)
  // @brief Disable the drop down box for data entry.
  //
  // Disables the drop down box for data entry.  Both disables the
  // form elements and greys-out the selection arrow.
  //
  // @param keepval Do not clear the text field if true.
  // @return None.
  //
  this.disable = function(keepval) {
    this.my_doctxt_border = this.my_doctxt.style.borderColor;
    this.my_doctxt.disabled = true;
    if (keepval !== true) this.my_doctxt.value = '';
    //this.my_doctxt.style.borderColor = "grey grey grey grey";
    this.disableButton();
    this.enabled = false;
  }

  // -----------------------------------------------------------------------
  // @fn is_enabled()
  // @brief Return if this drop down box is enabled.
  //
  // Return if this dop down box is enabled.
  //
  // @return True if this drop down box is enabled, false otherwise.
  //
  this.is_enabled = function() {
    return this.enabled;
  }

  // -----------------------------------------------------------------------
  // @fn toggle()
  // @brief Toggles the visability of the drop down selection box.
  //
  // Toggles the visability of the drop down selection box.  If the
  // the box is closed, then it is opened.  If the box is open, then
  // it is closed.
  //
  // @return None.
  //
  this.toggle = function() {
    if (this.is_open) {
      this.my_docspan.style.display = 'none';
      this.is_open = false;
    } else if (this.my_docsel.length > 0) {
      this.my_docspan.style.display = 'inline';
      this.is_open = true;
    }
  }

  // -----------------------------------------------------------------------
  // @fn close()
  // @brief Closes the drop down selection box.
  //
  // Closes the drop down selection box.  
  //
  // @return None.
  //
  this.close = function() {
    if (this.is_open) {
      this.my_docspan.style.display = 'none';
      this.is_open = false;
    }
  }

  // -----------------------------------------------------------------------
  // @fn open()
  // @brief Opens the drop down selection box.
  //
  // Opens the drop down selection box if the number of selection
  // options is greater than zero.  
  //
  // @return None.
  //
  this.open = function() {
    if ((!this.is_open)&&(this.my_docsel.length > 0)) {
      this.my_docspan.style.display = 'inline';
      this.is_open = true;
    }
  }

  // -----------------------------------------------------------------------
  // @fn sel_onchange()
  // @brief Collects the selected value and puts it in the text box.
  //
  // Meant to be called as an onChange event for the select field. 
  // Collects the selected value and puts it in the text box field,
  // and then closes the drop down box. 
  //
  // @return None.
  //
  this.sel_onchange = function() {
    this.close();
    //this.my_doctxt.value = this.my_docsel[this.my_docsel.selectedIndex].value;
  }
}

/*=======================================================================*\
|  @class DropDownEventsGroup()
|  @brief A class that supports basic DropDownEvents group behavior.
| 
|  A class that supports basic group behavior for DrowDownEvents.
| 
|  @return None.
\*======================================================================*/
function DropDownEventsGroup() {
  this.group = new Array();  // The group of DropDownEvents objects

  // -----------------------------------------------------------------------
  // @fn add(eid,dbox)
  // @brief Adds a DropDownEvents object to this group.
  //
  // Adds a DropDownEvents object to this group.
  //
  // @param eid The docid of the span enclosing the drop down box. 
  // @param dbox The DropDownEvents object associated with the eid.
  // @return None.
  //
  this.add = function(eid,dbox) {
    if ((eid != null)&&(dbox != null)) {
      this.group[eid] = dbox; 
      return true;
    }
    return false;
  }

  // -----------------------------------------------------------------------
  // @fn remove(eid)
  // @brief Removes a DropDownEvents object to this group.
  //
  // Removes a DropDownEvents object to this group.
  //
  // @param eid The docid of the span enclosing the drop down box to remove. 
  // @return None.
  //
  this.remove = function(eid) {
    var pos = 0;
    for (var key in this.group) {
      if (key == eid) {
        this.group.splice(pos,1);
        return true;
      } 
      pos++;
    }
    return false;
  }

  // -----------------------------------------------------------------------
  // @fn closeAll()
  // @brief Closes all the drop down in this group.
  //
  // Closes all the drop down in this group.
  //
  // @return None.
  //
  this.closeAll = function() {
    for (var key in this.group) this.group[key].close();
  }

  // -----------------------------------------------------------------------
  // @fn closeAllBut(eid)
  // @brief Closes all but the specified drop down in this group.
  //
  // Closes all but the specified down down in this group.
  //
  // @param eid The docid of the span enclosing the box to leave open. 
  // @return None.
  //
  this.closeAllBut = function(eid) {
    for (var key in this.group) {
      if (key != eid) this.group[key].close();
    }
  }
}
