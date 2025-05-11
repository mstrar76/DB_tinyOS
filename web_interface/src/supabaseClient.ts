import { createClient } from '@supabase/supabase-js';

// Load environment variables for Supabase URL and Anon Key
// These should be set in a .env file in the web_interface directory
// e.g., VITE_SUPABASE_URL="YOUR_SUPABASE_URL"
//       VITE_SUPABASE_ANON_KEY="YOUR_SUPABASE_ANON_KEY"
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Ensure environment variables are loaded
if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Supabase URL and Anon Key environment variables are not set.');
  // You might want to throw an error or handle this case appropriately
}

// Create a single Supabase client for interacting with your database
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Optional: Add a simple check to see if the client was created
if (supabase) {
  console.log('Supabase client initialized.');
}
