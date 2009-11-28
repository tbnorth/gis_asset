jQ = jQuery;

jQ(init_dirents);

jQuery.fn.extend(
  {
    localText: function() {
      var txt = '';
      this.contents().each( 
        function() { 
          if (this.nodeType == 3) {
            txt = txt + this.nodeValue;
          }
        }
      );
      return txt;
    }
  }
);
function init_dirents() {
    jQ('.dirent').bind('click', dirop);
}
function dirop(event) {
    // note - triggered by the dirent that exists at the start
    // as those added later don't have click() bound, but
    // the first one contains all the latter ones.

    var targ = jQ(event.target);
    if (event.ctrlKey) {  // reload
        targ.children().remove();
    }
    if (targ.children().length > 0) {
        if (targ.children(":hidden").length == 0) {
            targ.children().hide('fast');
            return;
        } else {
            targ.children("*").show('fast');
            return;
        }
    }
    var holder = jQ('<div class="dirent"/>');
    targ.append(holder);
    holder.hide();
    var path = targ.text();
    targ = targ.parent().parent();
    while (targ.parent().is('.dirent')) {
      path = targ.localText() + '/' + path;
      targ = targ.parent().parent();
    }
    holder.load('/dirent/'+path, null, 
      function() { holder.show('fast'); } );
}

