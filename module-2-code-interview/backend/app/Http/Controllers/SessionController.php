<?php

namespace App\Http\Controllers;

use App\Models\InterviewSession;
use App\Events\CodeUpdated;
use App\Events\LanguageChanged;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\Rule;

class SessionController extends Controller
{
    /**
     * Create a new interview session
     */
    public function create(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'language' => ['nullable', 'string', Rule::in([
                'javascript', 'typescript', 'python', 'java',
                'cpp', 'go', 'rust', 'php'
            ])],
            'code' => 'nullable|string',
        ]);

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
    public function updateCode(Request $request, string $sessionId): JsonResponse
    {
        $session = InterviewSession::where('session_id', $sessionId)->firstOrFail();

        $validated = $request->validate([
            'code' => 'required|string',
        ]);

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
    public function updateLanguage(Request $request, string $sessionId): JsonResponse
    {
        $session = InterviewSession::where('session_id', $sessionId)->firstOrFail();

        $validated = $request->validate([
            'language' => ['required', 'string', Rule::in([
                'javascript', 'typescript', 'python', 'java',
                'cpp', 'go', 'rust', 'php'
            ])],
        ]);

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
