window.onload = function() {
  Webcam.set({
      width: 320,
      height: 240,
      image_format: 'jpeg',
      jpeg_quality: 90
    });
  Webcam.attach( '#my_camera' );

  var counter = 0;
  var video = document.getElementById('video');
  //var canvas = document.getElementById('canvas');
  //var context = canvas.getContext('2d');

  var tracker = new tracking.ObjectTracker('face');
  tracker.setInitialScale(4);
  tracker.setStepSize(2);
  tracker.setEdgesDensity(0.1);

  tracking.track('#video', tracker, { camera: true });
  tracker.on('track', function(event) {
    event.data.forEach(function(rect) {
        //console.log("FACE Detected");
        //take_snapshot();
        counter = counter + 1;
        take_snapshot(counter);
        if(counter == 50) {
          counter = 0;
        }
    });
  });
};


//Code to handle taking the snapshot and displaying it locally
function take_snapshot(count) {
  // take snapshot and get image data
  Webcam.snap(function(data_uri) {
  // display results in page
  //console.log(data_uri);
  //console.log(data_uri);
    if(count == 1) {
      console.timeEnd("upload success");
      console.time("upload success");
      Webcam.upload( data_uri, 'auction/new', function(code, response) {
        document.getElementById('file').innerHTML =
          '<h2>Here is your image:</h2>' +
          '<img src="'+data_uri+'"/>';

        console.log("response: " + response);
        var json = JSON.parse(response);
        console.log("url: " + json.url);

        document.getElementById('file2').innerHTML =
          '<h2>Here is your ad:</h2>' +
          '<img src="'+json.url+'"/>';
        document.getElementById('text').style.display="";
      });
    }
  });
}
