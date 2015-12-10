$(function() {

    var tracker = new tracking.ObjectTracker('face');
    tracker.setInitialScale(4);
    tracker.setStepSize(2);
    tracker.setEdgesDensity(0.1);

    var counter = 0;
    var video = $('#video')[0];
    var canvas = $('#canvas')[0];

    tracker.on('track', function(event) {
        event.data.forEach(function() {
            counter = counter + 1;
            if (counter % 100 == 0) {
                console.log("uploading snapshot");
                take_snapshot(upload);
            }
        });
    });

    tracking.track('#video', tracker, { camera: true });

    function take_snapshot(callback) {
        canvas.getContext('2d').drawImage(video, 0, 0, 640, 480);
        var compression = 1;
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
            if (data['features']['clothing']) {
                data['features']['clothing'] = data['features']['clothing'].map(toCircle).join("");
            }

            var features = mapToTr(data['features']);
            $("#features").find("table").html(features.join("\n"));

            var matches = mapToTr(data['winner']['matches']);
            $("#matches").find("table").html(matches.join("\n"));

            console.log("Winner ad: ", data['winner']);
            $("#ad").attr("src", data['winner']['url']);
        });

        function mapToTr(m) {
            return Object.keys(m).map(function (key) {
                return "<tr><td>" + key + "</td><td>" + m[key] + "</td></tr>";
            });
        }

        function toCircle(color) {
            var styles = [
                "display: inline-block",
                "border-radius: 50%/50%",
                "width: 25px",
                "height: 25px",
                "background-color: " + color
            ];
            return "<span style='"+ styles.join(";") +"'></span>";
        }
    }

});
