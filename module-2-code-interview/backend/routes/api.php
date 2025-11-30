<?php

use App\Http\Controllers\SessionController;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

// Session Management
Route::post('/sessions', [SessionController::class, 'create']);
Route::get('/sessions/{interviewSession}', [SessionController::class, 'show']);
Route::put('/sessions/{interviewSession}/code', [SessionController::class, 'updateCode']);
Route::put('/sessions/{interviewSession}/language', [SessionController::class, 'updateLanguage']);
