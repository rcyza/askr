$( document ).ready(function() {
  console.log( 'ready!' );
  $( 'form' ).find( 'input,a,select,button,textarea' ).filter( ':visible' )[0].focus();

  $( 'body' ).on('keydown', 'input, select, textarea', function(e) {
    var self = $(this)
      , form = self.parents('form:eq(0)')
      , focusable
      , next
      ;
    if (e.keyCode == 13) {
        focusable = form.find( 'input,a,select,button,textarea' ).filter( ':visible' );
        next = focusable.eq(focusable.index(this)+1);
        if (next.length) {
            next.focus();
        } else {
            form.submit();
        }
        return false;
    }
  });

  $( 'input,select,textarea' ).focus(function() {
	$(this).parent().parent().addClass( 'curFocus' )
  });

  $( 'input,select,textarea' ).blur(function() {
    $(this).parent().parent().removeClass( 'curFocus' )
  });

  $( '.flagToggle' ).click(function() {
    $('#'+this.id.substring(7, this.id.length)).toggle();
  });
});



