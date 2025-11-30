<?php

namespace App\Events;

use App\Models\InterviewSession;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class LanguageChanged implements ShouldBroadcast
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(
        public InterviewSession $session
    ) {}

    /**
     * Get the channels the event should broadcast on.
     */
    public function broadcastOn(): Channel
    {
        return new Channel('session.' . $this->session->session_id);
    }

    /**
     * The event's broadcast name.
     */
    public function broadcastAs(): string
    {
        return 'language.changed';
    }

    /**
     * Get the data to broadcast.
     */
    public function broadcastWith(): array
    {
        return [
            'sessionId' => $this->session->session_id,
            'language' => $this->session->language,
            'timestamp' => now()->toIso8601String(),
        ];
    }
}
