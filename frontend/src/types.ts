export type ApiEnveloe<T> = {
    data: T;
    error: string  | null;
    meta: unknown;
}

export type TokenPair ={
    access_token: string;
    refresh_toke: string ;
    token_type: string;

};

export type User = {
    id: number;
    username: string;
    full_name: string;
    email: string;
    
};

export type  EventItem = {
    id: string;
    titlle: string;
    description: string;
    city: string;
    starts_at: string;
}