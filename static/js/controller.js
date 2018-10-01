$(document).ready(function() {
	var baseUrl = window.location.pathname;
	
	// Global Functions
	window.checkRoute = function(route) {
		if(baseUrl.includes(route)) {
			return true;
		} else {
			return false;
		}
	}

	window.getNationName = function(selector, code) {
		$.ajax({
			url: 'https://restcountries.eu/rest/v2/alpha/' + code,
			method: 'GET',
			success: function(res) {
				$(selector).attr('value', res.name.toUpperCase());
			},
			error: function(err) {
				$(selector).attr('value', "INVALID COUNTRY");
			}
		})
	}

	window.htmlEntities = function(str) {
	    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
	}

	window.confirm = function() {
		if($('#nationcheck').val() == "INVALID COUNTRY" || $('#issuecheck').val() == "INVALID COUNTRY" 
			|| $('#birthdate').val() == "Invalid date" || $('#expirydate').val() == "Invalid date" ) {
			$('#alertModal').modal('show');
			$('#alertMessage').text("Mohon input data yang sesuai!");
		} else {
			$('#confirmSaveDialog').modal('show');
		}
	}

	// Route Checker
	if(checkRoute("/dashboard")) {
		var today = new Date
		
		var datatable = $('#datatable').DataTable( {
			ajax: {
				url: '/api/manage',
				dataSrc: 'output'
			},
			dom: 'Bfrtip',
			buttons: [
				'copy',
				{
					extend: 'csv',
	                exportOptions: {
	                    columns: [ 0, 1, 2, 3, 4, 5, 6, 7 ]
	                }	
    			},  
				{
					extend: 'pdfHtml5',
					messageTop: 'Exported Data - ' + today,
	                exportOptions: {
	                    columns: [ 0, 1, 2, 3, 4, 5, 6, 7 ]
	                }	
    			}, 
				{
					extend: 'print',
					messageTop: 'Exported Data - ' + today,
	                exportOptions: {
	                    columns: [ 0, 1, 2, 3, 4, 5, 6, 7 ]
	                }	
    			}
			],
			columns: [
				{
					"data": "id",
					render: function (data, type, row, meta) {
						return meta.row + meta.settings._iDisplayStart + 1;
					}
				},
				{data: 'name'},
				{data: 'sex'},
				{
					data: 'birthdate',
					render: function (data, type, full, meta) {
						return moment(full.birthdate).format('DD/MM/YYYY');
					}
				},
				{data: 'passport_num'},
				{data: 'issue_n'},
				{data: 'nation_n'},
				{
					data: 'expirydate',
					render: function (data, type, full, meta) {
						return moment(full.birthdate).format('DD/MM/YYYY');
					}
				},
				{
					data: 'id',
					className: "center",
					render: function ( data, type, full, meta ) {
						return'<a href="edit/'+full._id+'" class="btn btn-secondary buttons-edit mr-2"><i class="fas fa-pencil-alt"></i> Edit</a>' +
						'<a href="delete/'+full._id+'" class="btn btn-secondary buttons-delete"><i class="fas fa-trash-alt"></i> Delete</a>';
					}
				}
			],
			"columnDefs": [
	            {
	                "targets": [2,5,6,7],
	                "visible": false,
	                "searchable": false
	            },
            ]
		});

		datatable.buttons().container()
		.appendTo( '#datatable_wrapper .col-md-12:eq(0)' );
	}

	else if(checkRoute("/upload")) {
		var tempRes, tempResPath;
		
		var image = $('#cropper-image');
		
		var cropper = image.cropper({
			aspectRatio: 550 / 378,
			responsive: true,
			dragMode: 'move',
			viewMode: 1,
		});

		$("#upload_image").dropzone({
			maxFiles: 2048,
			acceptedFiles: "image/*",
			uploadMultiple: false,
			success: function(file, res){
				this.removeFile(file);
				$('#editModal').modal('show');
				$('#editModal').on('shown.bs.modal', function(e){
					cropper.cropper('replace', res.path);
				});
				tempRes = res;
				tempResPath = res.image;
			},
			error: function(file, err) {
				this.removeFile(file);
				$('#alertModal').modal('show');
				$('#alertMessage').text("Gagal mengupload file karena anda mengupload gambar lebih dari 10MB atau ekstensi file tidak sesuai.");
			}
		});


		window.crop_image = function(){
			$('button#process_image').prop('disabled', true);
			$('button#process_image').html('<i class="fas fa-spinner fa-spin"></i> Mohon tunggu...');
			var croppedImage = cropper.cropper('getCroppedCanvas').toDataURL();
			var jsonImage = { 'image' : croppedImage, 'fileName' : tempResPath }			
			$.ajax({
				url: '/api/upload/process',
				type: 'POST',
				data: JSON.stringify(jsonImage),
				contentType: 'application/json',
				dataType : 'json',
				success: function(res) {
					$('#editModal').modal('hide');
					show_result(res);
					$('#upload_image').fadeOut();
				},
				error: function(err) {
					$('#upload_image').fadeIn();
					$('#editModal').modal('hide');
					$('#alertModal').modal('show');
					$('#alertMessage').text("Gagal memproses file! Mohon coba lagi.");
				},
				complete: function() {
					$('button#process_image').prop('disabled', false);
					$('button#process_image').html('Proses');
				}
			});
		}

		window.show_result = function(result) {
			$('#dataForm').fadeIn();
			
			// Mengubah kode negara jadi Nama Negara
			$('#nation').val(result['output'][4]);
			$('#issue').val(result['output'][1]);
			getNationName('#nationcheck',result['output'][4]);
			getNationName('#issuecheck',result['output'][1]);

			// Mengubah huruf jenis kelamin menjadi jenis kelamin lengkap
			if(result['output'][6].toUpperCase() == "F" ) 
				{ $('#sex').val("PEREMPUAN"); } 
			else if (result['output'][6].toUpperCase()  == "M")
				{ $('#sex').val("LAKI-LAKI"); }
			else { $('#sex').val("TIDAK DISEBUTKAN"); }

			$('#display_img').attr("src", result['path']);
			$('#name').val(result['output'][2]);
			$('#passport_num').val(result['output'][3]);
			$('#birthdate').val(moment(result['output'][5], "YYMMDD").format("DD/MM/YYYY"));
			$('#expirydate').val(moment(result['output'][7], "YYMMDD").format("DD/MM/YYYY"));
			$('#passport_image').val(result['image']);
			$('#passport_path').val(result['path']);
		};

		window.cancel = function() {
			$('#dataForm').fadeOut();
			$('#upload_image').fadeIn();
		}
	}

	else if (checkRoute("/reports")) {
		var datatable;
		$('#datepicker_from').datepicker({
			uiLibrary: 'bootstrap4'
		});

		$('#datepicker_to').datepicker({
			uiLibrary: 'bootstrap4'
		});

		$('#searchdata').on('click', function() {
			var datefrom = new Date($('#datepicker_from').val()).toISOString();
			var dateto = new Date($('#datepicker_to').val()).toISOString();
			$.get('api/report/'+datefrom+'/'+dateto, function(res) {
				if(!$.fn.DataTable.isDataTable('#datatable')) {
					datatable = $('#datatable').DataTable({
						autoWidth: false,
						processing: "true",
						data: res.results,
						dom: 'Bfrtip',
						buttons: [
		        			{
								extend: 'print',
								messageTop: 'Generated Report from ' + moment(datefrom).format('DD/MM/YYYY') + ' to ' + moment(dateto).format('DD/MM/YYYY'),
								exportOptions: {
									columns: [0,1,2],
									stripHtml: false
								}
							}
						],
						columns: [
							{
								"data": "id",
								render: function (data, type, row, meta) {
									return meta.row + meta.settings._iDisplayStart + 1;
								}
							},
							{
								data: 'image_path',
								render: function (data, type, row, meta) {
									return '<img id="imgToExport" class="img-fluid" src="' + data + '" style="width: 320px; height: auto">';
								}
							},
							{
								data: '_id',
								render: function (data, type, row, meta) {
									return '<p class="font-weight-bold m-0">No. Paspor: '+row.passport_num+'</p>' +
										'<p class="font-weight-bold m-0">Nama Lengkap: '+row.name+'</p>' +
										'<p class="font-weight-bold m-0">Negara yang Mengeluarkan: '+row.issue_n+'</p>' +
										'<p class="font-weight-bold m-0">Kewarganegaraan: '+row.nation_n+'</p>' +
										'<p class="font-weight-bold m-0">Tanggal Lahir: '+moment(row.birthdate).format('DD/MM/YYYY')+'</p>' +
										'<p class="font-weight-bold m-0">Jenis Kelamin: '+row.sex+'</p>' +
										'<p class="font-weight-bold m-0">Tanggal Kadaluarsa: '+moment(row.expirydate).format('DD/MM/YYYY')+'</p>';
								}
							},
						],
						"columnDefs": [ {
				            "searchable": false,
				            "orderable": false,
				            "targets": 0,
				        },

				         ],
				        "order": [[ 1, 'asc' ]]
					});

					datatable.on( 'order.dt search.dt', function () {
				        datatable.column(0, {search:'applied', order:'applied'}).nodes().each( function (cell, i) {
				            cell.innerHTML = i+1;
				        } );
				    } ).draw();
				} else {
					datatable.clear().draw();
					datatable.rows.add(res.results); // Add new data
					datatable.columns.adjust().draw(); // Redraw the DataTable
				}
				
			});
		});
	}

	else {

	}
});