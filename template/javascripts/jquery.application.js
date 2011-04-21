function pageLandingInteractions(context){

}

jQuery(document).ready(function($) {
  var context = '#page_landing';
  $(context).runOnScope(function(){
    var pageLanding = new pageLandingInteractions(context);
  });
});