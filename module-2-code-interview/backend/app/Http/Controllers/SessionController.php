<?php

namespace App\Http\Controllers;

use App\Models\InterviewSession;
use App\Events\CodeUpdated;
use App\Events\LanguageChanged;
use App\Http\Requests\CreateSessionRequest;
use App\Http\Requests\UpdateSessionCodeRequest;
use App\Http\Requests\UpdateSessionLanguageRequest;
use Illuminate\Http\JsonResponse;

class SessionController extends Controller
{
    /**
     * Create a new interview session
     */
    public function create(CreateSessionRequest $request): JsonResponse
    {
        $validated = $request->validated();

        $session = InterviewSession::create([
            'language' => $validated['language'] ?? 'javascript',
            'code' => $validated['code'] ?? '',
        ]);

        return response()->json($session, 201);
    }

    /**
     * Get session details
     */
    public function show(string $sessionId): JsonResponse
    {
        $session = InterviewSession::where('session_id', $sessionId)->firstOrFail();

        return response()->json($session);
    }

    /**
     * Update session code
     */
    public function updateCode(UpdateSessionCodeRequest $request, string $sessionId): JsonResponse
    {
        $session = InterviewSession::where('session_id', $sessionId)->firstOrFail();

        $validated = $request->validated();

        $session->update([
            'code' => $validated['code'],
        ]);

        // Broadcast the code update to all connected clients
        broadcast(new CodeUpdated($session))->toOthers();

        return response()->json($session);
    }

    /**
     * Update session language
     */
    public function updateLanguage(UpdateSessionLanguageRequest $request, string $sessionId): JsonResponse
    {
        $session = InterviewSession::where('session_id', $sessionId)->firstOrFail();

        $validated = $request->validated();

        $session->update([
            'language' => $validated['language'],
        ]);

        // Broadcast the language change to all connected clients
        broadcast(new LanguageChanged($session))->toOthers();

        return response()->json($session);
    }

    /**
     * Health check endpoint
     */
    public function health(): JsonResponse
    {
        return response()->json([
            'status' => 'ok',
            'timestamp' => now()->toIso8601String(),
        ]);
    }
}
