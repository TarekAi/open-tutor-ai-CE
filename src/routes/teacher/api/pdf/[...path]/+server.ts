import type { RequestHandler } from './$types'

export const GET: RequestHandler = async ({ params }) => {
    const backendUrl = `http://localhost:8080/uploads/${params.path}`
    const res = await fetch(backendUrl)
    const buffer = await res.arrayBuffer()
    return new Response(buffer, {
        headers: {
            "Content-Type": "application/pdf"
        }
    })
}