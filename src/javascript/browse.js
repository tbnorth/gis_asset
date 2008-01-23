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
    var holder = jQ('<div class="dirent"/>');
    var targ = jQ(event.target);
    targ.append(holder);
    var path = targ.text();
    targ = targ.parent().parent();
    while (targ.parent().is('.dirent')) {
      path = targ.localText() + '/' + path;
      targ = targ.parent().parent();
    }
    holder.load('/dirent/'+path);
}

