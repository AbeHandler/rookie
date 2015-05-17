function prepareData() {
  var data = {};

  data.search_input = encodeURIComponent($("#text-box").val());
  data.vendor = encodeURIComponent($('#vendors').val());
  data.department = encodeURIComponent($('#departments').val());
  data.officer = encodeURIComponent($('#officers').val());
  data.current_page = document.querySelector('#pagination');

  // console.log(document.querySelector('#pagination'));
  // console.log(typeof document.querySelector('#pagination'));

  if (data.current_page === null) {
    // console.log(data.current_page);
    // console.log(typeof data.current_page);
    data.current_page = 1;
  } else {
    // console.log(data.current_page);
    // console.log(typeof data.current_page);
    data.current_page = document.querySelector('#pagination').getAttribute('data-current-page');
  }

  console.log(data);

  return data;
}

function buildSearch(data) {
  var query_string = '?';

  if (data.search_input !== '') {
    query_string = query_string + "query=" + data.search_input;
  }

  if (data.vendor !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "vendor=" + data.vendor;
  }

  if (data.department !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "department=" + data.department;
  }

  if (data.officer !== '') {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "officer=" + data.officer;
  }

  if (data.current_page !== '' && data.current_page !== "1") {
    if (query_string !== '?') {
      query_string = query_string + '&';
    }
    query_string = query_string + "page=" + data.current_page;
  }

  if (query_string == '?') {
    query_string = "";
  }

  return query_string;
}

function setHandlers() {
  $("#next").on("click", function() {
    next();
  });

  $("#previous").on("click", function() {
    previous();
  });

  $(".search-button").on("click", function() {
    getSearch();
  });

  $(".open-button").on("click", function() {
    var id = $(this).parents(".contract-row").attr("id");
    window.location.href = '/contracts/contract/' + id;
  });

  $(".download").on("click", function() {
    var id = $(this).parents(".contract-row").attr("id");
    downloadFile("/contracts/download/" + id);
  });

  $("#advanced-search").on("click", function() {
    var display = document.getElementById("filters").style.display;
    if (display === "block") {
      document.getElementById('filters').style.display = 'none';
      document.getElementById('advanced-search').innerHTML = 'Show advanced search <i class="fa fa-caret-down"></i>';
    } else {
      document.getElementById('filters').style.display = 'block';
      document.getElementById('advanced-search').innerHTML = 'Hide advanced search <i class="fa fa-caret-up"></i>';
    }
  });
}

function populateSearchParameters(data) {
  console.log(data);
  //debugger;

  // document.getElementById('text-box').value = data.search_input;
  // document.getElementById('vendors').value = data.vendors;
  // document.getElementById('departments').value = data.departments;
  // document.getElementById('officers').value = data.officers;
}

function getSearch() {
  var data = prepareData();

  var query_string = buildSearch(data);
  console.log(query_string);
  
  window.location.href = '/contracts/search/' + query_string;
}

$(document).ready(function() {
  $(document).keypress(function(e) {
    if (e.which == 13) {
      getSearch();  // todo: Need to have GET at first, POST afterward.
    }
  });

  setHandlers();
});

// function checkForChanges() {
//   if ($('.t402-elided').length > 0) {
//     setTimeout(checkForChanges, 1000);
//     console.log('Trying again in one second.');
//   } else {
//     console.log('Survey completed or skipped. Adding in advancedsearch');
//     //var html = $("#blockOfStuff").html();
//     //$("#post-gcs").html(html);
//   }
// }
