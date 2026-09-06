import { revalidatePath } from 'next/cache';
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ detail: 'Not found' }, { status: 404 });
}

export async function POST(request: Request) {
  try {
    const body = (await request.json().catch(() => ({}))) as { path?: unknown };
    const path = typeof body.path === 'string' && body.path.startsWith('/') ? body.path : '/';
    revalidatePath(path);
    return NextResponse.json({ revalidated: true, path });
  } catch {
    return NextResponse.json({ detail: 'Not found' }, { status: 404 });
  }
}
