$(document).ready(function() {
    var search_box = $("div#search_box input[name=q]");
    var results_div = $("div#results");

    search_box.keyup(function(event){
    var q = search_box.val();
    if (q.length > 2) {
        $('div#partial').html('');
        getCachedJson('/autocomplete/movie/'+encodeURIComponent(q), function(json){
        var html = '';
        var ratings = {};
        $.each(json, function(id, item) {
            html = html + '<div class="movie" id="movie_'+item[0]+
                '" ><span class="span-14"><a class="title" href="/movie/' +
                item[0] + '-_" >' + item[1] +
                '</a></span><span class="rateit" ></span></div>';
            ratings[item[0]] = item[2];
        });

        results_div.html(html);
        $("span.rateit").rateit();
        $.each($("div.movie"), function(_, div){
            var movie_id = $(div).attr('id').replace('movie_','');
            $(div).find("span.rateit").rateit('value', ratings[movie_id]*.5);
        });

        $('div.movie :even').css('background-color', '#d7ebf9');
        });
    } else {
        results_div.html('');
    }
    });

});

$("span.rateit").live("rated", function() {
  var rater = $(this);
  var movie_id = rater.parents("div.movie").attr('id').replace('movie_','');
  var rating = rater.rateit('value')*2;
  $.post('/user/rate', {movie_id: movie_id, rating: rating}, function(response){});

});

$("span.rateit").live("reset", function() {
  var rater = $(this);
  var movie_id = rater.parents("div.movie").attr('id').replace('movie_','');
  $.post('/user/rate', {movie_id: movie_id, rating: 0}, function(response){});
});

var movie_partials = {};
$("div.movie").live("mouseenter", function() {
  var movie_id = $(this).attr("id").replace('movie_','');

  var partial = movie_partials[movie_id];
  if (partial) {
      $("div#partial").html(partial);

  } else {
    $.get('/movie/partial/'+movie_id, {}, function(response) {
      $("div#partial").html(response);
      movie_partials[movie_id] = response;
    });
  }

});
