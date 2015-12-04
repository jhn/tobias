$(function() {

    var tracker = new tracking.ObjectTracker('face');
    tracker.setInitialScale(4);
    tracker.setStepSize(2);
    tracker.setEdgesDensity(0.1);

    var counter = 0;
    var video = $('#video')[0];
    var canvas = $('canvas')[0];

    tracker.on('track', function(event) {
        event.data.forEach(function() {
            counter = counter + 1;
            if (counter % 40 == 0) {
                console.log("uploading snapshot");
                take_snapshot(upload);
            }
        });
    });

    tracking.track('#video', tracker, { camera: true });

    function take_snapshot(callback) {
        canvas.getContext('2d').drawImage(video, 0, 0, 320, 240);
        var compression = 0.90;
        return canvas.toBlob(callback, "image/jpeg", compression);
    }

    function upload(file) {
        var fd = new FormData();
        fd.append('file', file);
        $.ajax({
          url: 'simulation/new',
          data: fd,
          processData: false,
          contentType: false,
          type: 'POST',
          dataType: "json"
        }).done(function(data) {
            console.log("Image features: ", data.features);
            console.log("Winner ad: ", data.winner);
            $("#ad").attr("src", data.winner.url);
        });
    }

});