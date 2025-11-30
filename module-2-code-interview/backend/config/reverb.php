<?php

return [

    /*
    |--------------------------------------------------------------------------
    | Default Reverb Server
    |--------------------------------------------------------------------------
    */

    'default' => env('REVERB_SERVER', 'reverb'),

    /*
    |--------------------------------------------------------------------------
    | Reverb Servers
    |--------------------------------------------------------------------------
    */

    'servers' => [

        'reverb' => [
            'host' => env('REVERB_HOST', '0.0.0.0'),
            'port' => env('REVERB_PORT', 8080),
            'hostname' => env('REVERB_HOSTNAME', 'localhost'),
            'options' => [
                'tls' => [],
            ],
            'scaling' => [
                'enabled' => env('REVERB_SCALING_ENABLED', false),
                'channel' => env('REVERB_SCALING_CHANNEL', 'reverb'),
            ],
            'pulse_ingest_interval' => env('REVERB_PULSE_INGEST_INTERVAL', 15),
        ],

    ],

    /*
    |--------------------------------------------------------------------------
    | Reverb Applications
    |--------------------------------------------------------------------------
    */

    'apps' => [

        [
            'id' => env('REVERB_APP_ID', 'code-interview'),
            'key' => env('REVERB_APP_KEY', 'local-key'),
            'secret' => env('REVERB_APP_SECRET', 'local-secret'),
            'options' => [
                'host' => env('REVERB_HOST', '0.0.0.0'),
                'port' => env('REVERB_PORT', 8080),
                'scheme' => env('REVERB_SCHEME', 'http'),
            ],
            'allowed_origins' => ['*'],
            'ping_interval' => env('REVERB_PING_INTERVAL', 15),
            'max_message_size' => env('REVERB_MAX_MESSAGE_SIZE', 10000),
        ],

    ],

];
