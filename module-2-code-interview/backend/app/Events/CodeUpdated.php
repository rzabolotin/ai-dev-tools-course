<?php

namespace App\Events;

use App\Models\InterviewSession;
use Illuminate\Broadcasting\Channel;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Contracts\Broadcasting\ShouldBroadcast;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class CodeUpdated implements ShouldBroadcast
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
        return 'code.updated';
    }

    /**
     * Get the data to broadcast.
     */
    public function broadcastWith(): array
    {
        return [
            'sessionId' => $this->session->session_id,
            'code' => $this->session->code,
            'timestamp' => now()->toIso8601String(),
        ];
    }
}
