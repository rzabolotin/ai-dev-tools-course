<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Str;

class InterviewSession extends Model
{
    use HasFactory;

    protected $fillable = [
        'session_id',
        'code',
        'language',
    ];

    protected static function boot()
    {
        parent::boot();

        static::creating(function ($session) {
            if (empty($session->session_id)) {
                $session->session_id = Str::random(16);
            }
        });
    }

    public function getRouteKeyName()
    {
        return 'session_id';
    }
}
