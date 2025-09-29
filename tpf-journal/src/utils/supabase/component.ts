import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  // console.log(process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!)
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  )

  return supabase
}

//  export const supabase = createBrowserClient(
//     process.env.NEXT_PUBLIC_SUPABASE_URL!,
//     process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
//   )

