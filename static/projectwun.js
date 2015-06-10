// PART 1: SHOW Book results

function getBookResults(evt) {
  evt.preventDefault();
  $('#results-div').empty();
  $('#book-result-div').empty();

    // With JQuery
  

  var url = "/search?" + $('.user_book_query').serialize(); 
  $.get(url, function(json) { 
    $('#logo').append('<img src="./static/img/wunderland_logo.png">');
    $('#book-results-background').show();
    var searchInput = $("#search-input").val();
    var radius = $('radius-dropdown').val();
    $('#wunderland_full').remove();
    var searchForm = $('#search-input-form').html();
    $('#search-input-form').remove();
    $('#navbar-search').append(searchForm);

    $("#results-div").append("<p id='results-line'>Found <em>" + json.name.length + "</em> books associated with <em>" + searchInput + ".</p>"); 
    $('.results-tabs').addClass('show');
    for (var book=0; book <json.name.length; book++) {
     
      $("#book-result-div").append('<div class="col-md-3"><a data-toggle="modal" data-target="#myModal" href="#"><img id="' +
        json.name[book].isbn + '" class="book-thumbnail" data-title="' +
         json.name[book].title + '" data-keywords="' + 
         json.name[book].keywords + '" data-subtitle="' + 
         json.name[book].subtitle + '" data-thumbnail="' + 
         json.name[book].thumbnailUrl + '" data-description="' + 
         json.name[book].description +'" data-author="' + 
         json.name[book].authors + '" src="' + 
         json.name[book].thumbnailUrl + '"></a></div>'
      );   
    }

    $(".book-thumbnail").click(function() {
      
      $('.book-title').empty();
      $('.book-keywords').empty();
      $('.book-subtitle').empty();
      $('.book-author').empty();
      $('.book-thumbnailUrl').empty();
      $('.book-description').empty();

      var keywords = ($(this).data("keywords")).split(",");
      for (var word=0; word<keywords.length; word++) {
        // var keywordUrl = "/keyword/" + $(keyword[word]).serialize.();
        $(".book-keywords").append('<button type="button" class="btn btn-xs tester keywordbutton" data-key="' +
          keywords[word] + '">' + keywords[word] + "</button>" + " ")
   
      }
      $(".book-title").append($(this).data("title"));
      $('.book-subtitle').append($(this).data('subtitle'));
      $('.book-author').append($(this).data('author'));
      $('.book-description').append($(this).data('description'));
      $('.book-thumbnailUrl').append("<img class='modal-cover' src='" + ($(this).data('thumbnail')) + "'>");

    }); 
    
  });
}

// The end of getBookResults //



// Part 2: Get Keyword Associated Books
 

$(document).on('click', '.keywordbutton', function() {
  $('#results-div').empty();
  $('#book-result-div').empty();


  var keyword = $(this).data('key');
  var url = "/keyword?keyword=" + keyword
  
  console.log(keyword)
  console.log(url)

  $.get(url, function(json) {


    $("#results-div").append("<p id='keyword-line'>Found <em>" + json.keywordbooks.length + 
    "</em> books associated with <em>" + keyword + "</em>.</p>"); 

    $('.results-tabs').addClass('show');

    for (var book=0; book <json.keywordbooks.length; book++) {
     
      $("#book-result-div").append('<div class="col-md-3"><a data-toggle="modal" data-target="#myModal" href="#"><img id="' +
        json.keywordbooks[book].isbn + '" class="book-thumbnail" data-title="' +
         json.keywordbooks[book].title + '" data-keywords="' + 
         json.keywordbooks[book].keywords + '" data-subtitle="' + 
         json.keywordbooks[book].subtitle + '" data-thumbnail="' + 
         json.keywordbooks[book].thumbnailUrl + '" data-description="' + 
         json.keywordbooks[book].description +'" data-author="' + 
         json.keywordbooks[book].authors + '" src="' + 
         json.keywordbooks[book].thumbnailUrl + '"></a></div>'
      );   // append closer

      $(".book-thumbnail").click(function() {
      
      $('.book-title').empty();
      $('.book-keywords').empty();
      $('.book-subtitle').empty();
      $('.book-author').empty();
      $('.book-thumbnailUrl').empty();
      $('.book-description').empty();

      var keywords = ($(this).data("keywords")).split(",");
      for (var word=0; word<keywords.length; word++) {
        // var keywordUrl = "/keyword/" + $(keyword[word]).serialize.();
        $(".book-keywords").append('<button type="button" class="btn btn-success btn-xs tester keywordbutton" data-key="' +
          keywords[word] + '">' + keywords[word] + "</button>" + " ")
   
      }
      $(".book-title").append($(this).data("title"));
      $('.book-subtitle').append($(this).data('subtitle'));
      $('.book-author').append($(this).data('author'));
      $('.book-description').append($(this).data('description'));
      $('.book-thumbnailUrl').append("<img class='modal-cover' src='" + ($(this).data('thumbnail')) + "'>");

      }); // modals book-thumbnail 
    } // for loop closing
  }); // get request closer
});  // bookthumbnail click closer
// }    // outermost bracket





function getModalInfoForEachBook(evt) {
  console.log("something there")
  $('.book-title').empty();
  $('.book-keywords').empty();

  var url='/search?' + $('.user_book_query').serialize();

  $.get(url, function(json) {
    console.log(json)
  })
}


function getKMeansResults(evt) {
  evt.preventDefault();
  $('#results-div').empty();
  $('#book-result-div').empty();
  $('#kmeans_graph').empty();    

  var url = "/search/kmeans?" + $('.user_book_query').serialize();

  $.get(url, function(json) { 
    $("#kmeans_graph").append(json.kmeans); 
    // console.log(json.kmeans)
  });
}


// Part 3: Geolocation for LocalVenues



function successFunction(position) { 
  $('#local_venues').empty();
    var lat = position.coords.latitude;
    var lon = position.coords.longitude;
    var url = "/location?lat=" + lat + "&" + "lon=" + lon
    console.log('Your latitude is :'+lat+' and longitude is '+lon);
    var coords = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
    
    
  $.get(url, function(json) {
    console.log(json.localVenues)
    var bookStores = json.localVenues
    $('a[aria-controls="#venues"]').on('shown.bs.tab', function (e) {
      initialize(coords, bookStores);
    }); // end of venues tab show
      
    console.log(bookStores)
  }); //end of get   
  
} // end of successFunction

function errorFunction(position) {
  $('#local_venues').empty();
  flash('Error!');
}


// Google Custom Map

  

var styles = [{"stylers":[{"saturation":-100}]},{"featureType":"water","elementType":"geometry.fill","stylers":[{"color":"#0099dd"}]},
{"elementType":"labels","stylers":[{"visibility":"off"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#aadd55"}]},
{"featureType":"road.highway","elementType":"labels","stylers":[{"visibility":"on"}]},{"featureType":"road.arterial","elementType":"labels.text","stylers":[{"visibility":"on"}]},
{"featureType":"road.local","elementType":"labels.text","stylers":[{"visibility":"on"}]},{}];



function initialize(coords, bookStores) {
  console.log("in initialize")
  console.log(coords)
  var mapProp = {
      center:coords,
      zoom: 15,
      draggable: false,
      scrollwheel: false,
      mapTypeControl:false,
      navigationControlOptions: {
      style: google.maps.NavigationControlStyle.SMALL
      },
      mapTypeId:google.maps.MapTypeId.ROADMAP
  };

  // Add markers to the map

  // Marker sizes are expressed as a Size of X,Y
  // where the origin of the image (0,0) is located
  // in the top left of the image.
  // Origins, anchor positions and coordinates of the marker
  // increase in the X direction to the right and in
  // the Y direction down.
  var bookIcon = {
    path: "M 461.754,51.435c0-3.902-1.822-7.581-4.927-9.945c-3.105-2.364-7.132-3.144-10.896-2.105L230.877,98.694L15.823,39.384 c-3.762-1.037-7.792-0.258-10.896,2.105C1.823,43.853,0,47.531,0,51.434v298.615c0,5.624,3.755,10.555,9.177,12.05l216.934,59.829 c1.468,0.583,3.031,0.892,4.611,0.892c0.052,0,0.104-0.005,0.155-0.006c0.052,0.001,0.104,0.006,0.154,0.006 c1.58,0,3.143-0.309,4.609-0.891L452.577,362.1c5.422-1.495,9.177-6.427,9.177-12.05V51.435z M25,67.849l193.221,53.289v272.683 L25,340.53V67.849z M436.754,340.53l-193.221,53.29V121.138l193.221-53.289V340.53 z",
    fillColor: '#000000',
    fillOpacity: 0.8,
    scale: 0.05,
    strokeColor: 'black',
    strokeWeight: 2,
    // This marker is 1 pixels wide by 4 pixels tall.
    size: new google.maps.Size(1,4),
    // The origin for this image is 0,0.
    origin: new google.maps.Point(0,0),
    // The anchor for this image is the base of the book at 0,32.
    anchor: new google.maps.Point(0,32)
  };
  // Shapes define the clickable region of the icon.
  // The type defines an HTML &lt;area&gt; element 'poly' which
  // traces out a polygon as a series of X,Y points. The final
  // coordinate closes the poly by connecting to the first
  // coordinate.
  var shape = {
      coords: [1, 1, 1, 20, 18, 20, 18 , 1],
      type: 'poly'
  };

  var map = new google.maps.Map(document.getElementById("map-canvas"),mapProp);
  map.setOptions({styles: styles});

  for (var i = 0; i < bookStores.length; i++) {
    var bookstore = bookStores[i];
    var myLatLng = new google.maps.LatLng(bookstore[1], bookstore[2]);
    var marker = new google.maps.Marker({
        position: myLatLng,
        map: map,
        icon: bookIcon,
        shape: shape,
        title: bookstore[0],
        website: bookstore[4],
        zIndex: bookstore[3]
    


    }); //end of marker creation
  } //end of bookSTore for loop

  // Creating an InfoWindow object
  infowindow = new google.maps.InfoWindow({
    content: "holding..."
  });

  for (var i = 0; i < markers.length; i++) {

    var marker = markers[i];
      google.maps.event.addListener(marker, 'click', function () {

      // where I have added .html to the marker object.
      infowindow.setContent(this.html);
      infowindow.open(map, this);
    }); //end of addlistener for marker
    
  } //end of for loop for markers.length


  
}; //end of the initialize function



// DOCUMENT READY 
$(document).ready(function () {
  $('.user_book_query').on('submit', getBookResults);
  $('.user_book_query').on('submit', getKMeansResults);
  
  
  $('.user_book_query').on('submit', function() {

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(successFunction);

  } else {
    flash('It seems like Geolocation, which is required for this page, is not enabled in your browser. Please use a browser which supports it.');
  }
  }); // geolocation test


  $('#books').tab('show');

  $('#myTab a:first').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
  });

  $('#myTab a:nth-child(2)').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
  });

  $('#myTab a:last').click(function (e) {
    e.preventDefault()
    $(this).tab('show')
  });




  // The timer for the loading screen - starts 1000 ms after call
  $(document).ajaxStart(function () {
      timer = setTimeout(function () {
        $("#loaderthingy").show();
      }, 1000);
  });

  $(document).ajaxComplete(function () {
      $("#loaderthingy").hide();
      clearTimeout(timer);
  });

  $('#local_venues').ajaxStart(function() {
    timer = setTimeout(function() {
      $('#loaderthingy').show();
    }, 1000);
  });

  $('#local_venues').ajaxComplete(function () {
      $("#loaderthingy").hide();
      clearTimeout(timer);
  });

  $('.tester').on('click', function() {
  console.log("what'sup");
  });


}) // END


