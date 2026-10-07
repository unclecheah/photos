import { defineConfig } from 'vite';

export default defineConfig({
	server: {
		port: 3000,         // Dev server port
		strictPort: true,
		open: true,         // Open browser automatically when you run dev
		proxy: {
			'/api/': { target: 'http://127.0.0.1:8080' },
			'/data/': { target: 'http://127.0.0.1:8080' }
		}
	},
});
