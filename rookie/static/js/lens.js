function changeBannerImage() {
  // console.log('changeBannerImage');
  var header_img;
  var screenWidth = document.documentElement.clientWidth;

  if (screenWidth <= 500) {
    header_img = 'https://s3-us-west-2.amazonaws.com/lensnola/realestate/css/images/lens-logo-magnifying-glass-only.png';
    document.getElementById('banner-image').src = header_img;
    document.getElementById('banner-image').width = '35';
    document.getElementById('banner-logo').style.width = '40px';
    document.getElementById('banner-logo').style.marginTop = '0px';
  } else {
    header_img = 'https://s3-us-west-2.amazonaws.com/lensnola/realestate/css/images/lens-logo-retina.png';
    document.getElementById('banner-image').src = header_img;
    document.getElementById('banner-image').width = '100';
    document.getElementById('banner-logo').style.width = '100px';
    document.getElementById('banner-logo').style.marginTop = '5px';
  }

  if (screenWidth <= 600) {
    document.getElementById('banner-title').innerHTML = 'City contracts';
  } else {
    document.getElementById('banner-title').innerHTML = 'City of New Orleans contracts';
  }
}

var window_resize_timeout;

window.addEventListener('resize', function(e) {
  clearTimeout(window_resize_timeout);
  window_resize_timeout = setTimeout(changeBannerImage, 100);
});

changeBannerImage();
