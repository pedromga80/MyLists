

// --- Add the media to the user ---------------------------------------
function addToUser(element_id, media_type) {
    let category;

    if (media_type === 'movieslist') {
       category = 'Plan to Watch';
    } else {
       category = 'Watching';
    }

    $.ajax ({
        type: "POST",
        url: "/add_element",
        contentType: "application/json",
        data: JSON.stringify({element_id: element_id, element_type: media_type, element_cat: category}),
        dataType: "json",
        success: function() {
            $('#medialist-info').prepend(
                '<div class="alert alert-success m-t-15">' +
                    'Media successfully added to your list' +
                '</div>'
            );

            $('#your-medialist-data').show();
            $('#addlist').hide();
            $('#removeList').show();

            $('.alert').delay(2000).fadeOut(300, function() { $(this).remove(); });
        },
        error: function() {
            error_ajax_message('Unexpected error: The media could not be added. Please try again later.');
        }
    });
}


// --- Remove the media to the user ------------------------------------
function removeFromUser(element_id, media_type) {
    $.ajax ({
        type: "POST",
        url: "/delete_element",
        contentType: "application/json",
        data: JSON.stringify({ delete: element_id, element_type: media_type }),
        dataType: "json",
        success: function() {
            $('#medialist-info').prepend(
                '<div class="alert alert-warning m-t-15">' +
                    'Media removed from your list' +
                '</div>'
            );

            if (media_type === 'movieslist') {
                $('#category-dropdown').val('Plan to Watch');
            } else {
                $('#category-dropdown').val('Watching');
                $('#season-dropdown').val("0");
                $('#episode-dropdown').val("0");
            }

            $('#your-medialist-data').hide();
            $('#removeList').hide();
            $('#addlist').show();

            $('.alert').delay(2000).fadeOut(300, function() { $(this).remove(); });
        },
        error: function() {
            error_ajax_message('Error: The media could not be removed from your list. Please try again later.');
        }
    });
}


// --- Set media to favorite -------------------------------------------
function addFavorite(element_id, media_type) {
    let favorite;

    favorite = !!$('#favorite').hasClass('far');

    $.ajax ({
        type: "POST",
        url: "/add_favorite",
        contentType: "application/json",
        data: JSON.stringify({ element_id: element_id, element_type: media_type, favorite: favorite }),
        dataType: "json",
        success: function() {
            if ($('#favorite').hasClass('far')) {
                $('#favorite').addClass('fas').removeClass('far');
                $('#medialist-info').prepend(
                    '<div class="alert alert-success m-t-15">' +
                        'Added to your favorite' +
                    '</div>'
                );
            }
            else {
                $('#favorite').addClass('far').removeClass('fas');
                $('#medialist-info').prepend(
                    '<div class="alert alert-warning m-t-15">' +
                        'Removed from your favorite' +
                    '</div>'
                );
            }
            $('.alert').delay(2000).fadeOut(300, function() { $(this).remove(); });
        },
        error: function() {
            error_ajax_message('Error updating your favorite status. Please try again later.');
        }
    });
}


// --- Change the TV category ------------------------------------------
function changeCategoryTV(element_id, cat_selector, seas_data, media_list) {
    let new_cat, season_data, episode_drop, seasons_length, seasons_index, opt, i;

    new_cat = cat_selector.options[cat_selector.selectedIndex].value;

    $('#season-row').show();
    $('#episode-row').show();

    if (new_cat === 'Completed') {
        season_data = JSON.parse("["+seas_data+"]");
        episode_drop = document.getElementById('episode-dropdown');
        seasons_length = $('#season-dropdown').children('option').length;
        seasons_index = (seasons_length - 1);
        $('#season-dropdown').prop('selectedIndex', seasons_index);

        episode_drop.length = 1;

        for (i = 2; i <= season_data[0][seasons_index]; i++) {
            opt = document.createElement("option");
            opt.className = "";
            opt.innerHTML = '&nbsp;'+i+'&nbsp;';
            episode_drop.appendChild(opt);
        }
        $('#episode-dropdown').prop('selectedIndex', season_data[0][seasons_index]-1);
    }
    else if (new_cat === 'Random') {
        $('#season-row').hide();
        $('#episode-row').hide();
    }
    else if (new_cat === 'Plan to Watch') {
        $('#season-row').hide();
        $('#episode-row').hide();
    }

    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_cat, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            console.log("ok");
        },
        error: function() {
            error_ajax_message('Error changing your media status. Please try again later.');
        }
    });
}


// --- Change the Movie category ---------------------------------------
function changeCategoryMovies(element_id, cat_selector, genres) {
    let new_cat;

    new_cat = cat_selector.options[cat_selector.selectedIndex].value;

    if (new_cat === 'Completed') {
        if (genres.includes("Animation")) {
            new_cat = 'Completed Animation';
        }
    }

    $.ajax ({
        type: "POST",
        url: "/change_element_category",
        contentType: "application/json",
        data: JSON.stringify({status: new_cat, element_id: element_id, element_type: 'movieslist' }),
        dataType: "json",
        success: function() {
            console.log('ok');
        },
        error: function() {
            error_ajax_message('Error changing your media status. Please try again later.');
        }
    });
}


// --- Update season ---------------------------------------------------
function updateSeason(element_id, value, seas_data, media_list) {
    let season_data, selected_season, i, opt;

    season_data = JSON.parse("["+seas_data+"]");
    selected_season = value.selectedIndex;
    $('#episode-dropdown').length = 1;

    for (i = 2; i <= season_data[0][selected_season]; i++) {
        opt = document.createElement("option");
        opt.className = "";
        opt.text = i;
        $('#episode-dropdown').appendChild(opt);
    }

    $.ajax ({
        type: "POST",
        url: "/update_element_season",
        contentType: "application/json",
        data: JSON.stringify({season: selected_season, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            console.log("ok");
        },
        error: function() {
            error_ajax_message('Error updating the season of the media. Please try again later.');
        }
    });
}


// --- Update episode --------------------------------------------------
function updateEpisode(element_id, episode, media_list) {
    $.ajax ({
        type: "POST",
        url: "/update_element_episode",
        contentType: "application/json",
        data: JSON.stringify({episode: episode.selectedIndex, element_id: element_id, element_type: media_list }),
        dataType: "json",
        success: function() {
            console.log("ok");
        },
        error: function() {
            error_ajax_message('Error updating the episode of the media. Please try again later.');
        }
    });
}


// --- Lock the media --------------------------------------------------
function lock_media(element_id, element_type) {
    let lock_status;

    lock_status = $('#lock-button').prop("checked") === true;

    $.ajax ({
        type: "POST",
        url: "/lock_media",
        contentType: "application/json",
        data: JSON.stringify({element_id: element_id, element_type: element_type, lock_status: lock_status }),
        dataType: "json",
        success: function() {
            if ($('#lock-button').prop("checked") === true) {
                $('#lock-button-label').text('Media is Locked');
                $('#edit-button').attr('style', 'display: "";');
            } else {
                $('#lock-button-label').text('Media is Unlocked');
                $('#edit-button').attr('style', 'display: none;');
            }
        },
        error: function() {
            error_ajax_message('Error trying to lock the media. Please try again later.');
        }
    });
}


// --- Random box color ------------------------------------------------
$(document).ready(function () {
    let colors, boxes, i;
    colors = ['#6e7f80', '#536872', '#708090', '#536878', '#36454f'];
    boxes = document.querySelectorAll(".box");

    for (i = 0; i < boxes.length; i++) {
        boxes[i].style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
    }
});
