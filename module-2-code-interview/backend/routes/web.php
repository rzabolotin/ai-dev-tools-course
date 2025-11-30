<?php

use App\Http\Controllers\SessionController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
*/

Route::get('/health', [SessionController::class, 'health']);
