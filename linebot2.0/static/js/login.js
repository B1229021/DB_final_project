// $('#login-form').on('submit', function(e) {
//     e.preventDefault();

//     const line_id    = $('#line_id').val();
//     const u_id = $('#u_id').val();
//     const department = $('#department').val();

//     $.ajax({
//         type: 'POST',
//         url: 'http://localhost/linebot2.0/action.php?act=save_user',
//         data: {
//             // line_id: line_id,
//             u_id: u_id,
//             department: department
//         },
//         dataType: 'json',
//         success: function(response) {
//             if (response.status === "success") {
//                 alert(response.message);
//             } else {
//                 alert("錯誤：" + response.message);
//             }
//         },
//         error: function(xhr, status, error) {
//             console.error("AJAX Error: ", error);
//         }
//     });
// });
