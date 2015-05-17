function previous() {
  var current_page = $('#pagination').attr('data-current-page');
  current_page = current_page.toString();

  var number_of_pages = $('#pagination').attr('data-number-of-pages');
  number_of_pages = number_of_pages.toString();

  if (current_page === '1' || current_page === '0') {
    return;
  }

  var new_current_page = parseInt($("#pagination").attr("data-current-page"), 10) - 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);

  getSearch();
}

function next() {
  var current_page = $('#pagination').attr('data-current-page');
  current_page = current_page.toString();

  var number_of_pages = $('#pagination').attr('data-number-of-pages');
  number_of_pages = number_of_pages.toString();

  if (current_page === number_of_pages) {
    return;
  }

  var new_current_page = parseInt($("#pagination").attr("data-current-page"), 10) + 1;
  document.querySelector('#pagination').setAttribute('data-current-page', new_current_page);
  
  getSearch();
}

function checkPagerButtons() {//current_page, number_of_pages) {
  var current_page;
  var number_of_pages;

  if (typeof current_page === 'undefined') {
    current_page = $('#pagination').attr('data-current-page');
  }

  if (typeof number_of_pages === 'undefined') {
    number_of_pages = $('#pagination').attr('data-number-of-pages');
  }

  current_page = current_page.toString();
  number_of_pages = number_of_pages.toString();

  if (current_page === '1' || current_page === '0') {
    document.getElementById('previous').style.color = 'gray';
    document.getElementById('previous').style.cursor = 'default';
  } else {
    document.getElementById('previous').style.color = '#222';
    document.getElementById('previous').style.cursor = 'pointer';
  }

  if (current_page === number_of_pages) {
    document.getElementById('next').style.color = 'gray';
    document.getElementById('next').style.cursor = 'default';
  } else {
    document.getElementById('next').style.color = '#222';
    document.getElementById('next').style.cursor = 'pointer';
  }
}

$(document).ready(function() {
  checkPagerButtons();
});
