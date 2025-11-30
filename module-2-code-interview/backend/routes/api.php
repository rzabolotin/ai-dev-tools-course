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
Route::get('/sessions/{sessionId}', [SessionController::class, 'show']);
Route::put('/sessions/{sessionId}/code', [SessionController::class, 'updateCode']);
Route::put('/sessions/{sessionId}/language', [SessionController::class, 'updateLanguage']);
