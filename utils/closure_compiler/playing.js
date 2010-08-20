goog.require('goog.graphics');
goog.require('goog.events');
goog.require('goog.events.KeyCodes');
goog.require('goog.events.KeyHandler');


    var graphics = goog.graphics.createGraphics(1400, 850);

    // define the colors for the squares and the dot
    var square_fill = new goog.graphics.SolidFill('yellow');
    var square_stroke = new goog.graphics.Stroke(2, 'green');
    var dot_fill = new goog.graphics.SolidFill('blue');
    var dot_stroke = new goog.graphics.Stroke(1, 'black');

    // the dot's initial position
    var dot = {x: 1, y: 1};

    // properties    
    var size = 40;
    var margin = 5;
    var width = size - margin;
    var num_rows = 20;
    var num_cols = 30;

    // draw the squares
    for (var x = 0; x < num_cols; x++) {
        for (var y = 0; y < num_rows; y++) {
            graphics.drawRect(
                        margin + x * size,
                        margin + y * size,
                        width,
                        width,
                        square_stroke,
                        square_fill);
        }
    }

    // draw the dot
    dot['graphic'] = graphics.drawEllipse(
                                margin + dot['x'] * size + width / 2,
                                margin + dot['y'] * size + width / 2,
                                width / 4,
                                width / 4,
                                dot_stroke,
                                dot_fill);
    
    // call if the dot's position changes
    redraw_dot = function() {
        dot['graphic'].setCenter(
                            margin + dot['x'] * size + width / 2,
                            margin + dot['y'] * size + width / 2);
    }
    
    // key event handler
    var key_handler = new goog.events.KeyHandler(document);
    var key_event = function (e) {
        if (e.keyCode == goog.events.KeyCodes.UP && dot['y'] > 0) {
            dot['y'] -= 1;
        }
        else if (e.keyCode == goog.events.KeyCodes.RIGHT && dot['x'] <= num_cols - 2) {
            dot['x'] += 1;
        }
        else if (e.keyCode == goog.events.KeyCodes.DOWN && dot['y'] <= num_rows - 2) {
            dot['y'] += 1;
        }
        else if (e.keyCode == goog.events.KeyCodes.LEFT && dot['x'] > 0) {
            dot['x'] -= 1;
        }
        redraw_dot();
    }
    
    // put everything together
    goog.events.listen(key_handler, 'key', key_event);
    graphics.render(document.getElementById('shapes'));
