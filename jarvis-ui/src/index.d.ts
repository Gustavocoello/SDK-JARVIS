// src/index.d.ts
import { ReactNode, FC } from 'react';

// ============================================================
// TIPOS BASE
// ============================================================
export interface Chat {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  summary?: string;
}

export interface Message {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant';
  content: string;
  html?: string;
  stable?: boolean;
  created_at?: string;
}

export interface User {
  id: string;
  clerk_id: string;
  email: string;
  fullName: string;
  auth_provider: string;
  imageUrl?: string;
}

// ============================================================
// JARVIS PROVIDER
// ============================================================
export interface JarvisConfig {
  baseURL: string;
  getToken: () => Promise<string>;
  appId?: string;
  theme?: 'dark' | 'light';
  user?: Partial<User>;
  isLoaded?: boolean;
  logout?: () => void;
}

export interface JarvisProviderProps {
  children: ReactNode;
  config: JarvisConfig;
}

export declare const JarvisProvider: FC<JarvisProviderProps>;

// ============================================================
// CONTEXT
// ============================================================
export interface JarvisContextValue {
  version: string;
  client: any;
  getToken: () => Promise<string>;
  isAuthenticated: boolean;
  isInitializing: boolean;
  showAuthConfirm: boolean;
  user: User | null;
  logout: () => void;
  serviceConnections?: Record<string, boolean>;
  setServiceConnections?: (connections: any) => void;
  connectGoogleCalendar?: () => Promise<void>;
}

export declare function useJarvis(): JarvisContextValue;

// ============================================================
// CORE — chatApi
// ============================================================
export declare function getAllChats(client: any): Promise<Chat[]>;
export declare function getChatMessages(client: any, chatId: string): Promise<Message[]>;
export declare function fetchChatMessages(client: any, chatId: string): Promise<Message[]>;
export declare function createChat(client: any, data?: { title?: string }): Promise<Chat>;
export declare function deleteChat(client: any, chatId: string): Promise<void>;
export declare function updateChatTitle(client: any, chatId: string, title: string): Promise<Chat>;

// ============================================================
// CORE — stream
// ============================================================
export declare function sendMessage(
  payload: { chatId: string; text: string; hidden_context?: string; tool?: string },
  onPartialResponse: ((partial: string) => void) | null,
  signal: AbortSignal | undefined,
  client: any,
  getToken: () => Promise<string>
): Promise<string>;

export declare function sendAnonymousMessage(promptText: string, client: any): Promise<any>;
export declare function extractFileContent(file: File, client: any, getToken: () => Promise<string>): Promise<any>;

// ============================================================
// CORE — events
// ============================================================
export interface ChatEventEmitter {
  on(event: string, callback: (data?: any) => void): () => void;
  emit(event: string, data?: any): void;
}

export declare const chatEvents: ChatEventEmitter;

// ============================================================
// HOOKS
// ============================================================
export declare function useChatState(): {
  activeChatId: string | null;
  setActiveChatId: (id: string | null) => void;
  localMessages: Message[];
  setLocalMessages: (msgs: Message[]) => void;
  hasSentMessage: boolean;
  setHasSentMessage: (value: boolean) => void;
  resetChat: () => void;
};

export interface UseChatMessagesOptions {
  limit?: number;
  keep?: number;
  maxChats?: number;
  enabled?: boolean;
  offlineMode?: boolean;
  client: any;
}

export declare function useChatMessages(
  chatId: string | null,
  options: UseChatMessagesOptions
): {
  messages: Message[];
  lastUserMessageId: string | null;
  isSuccess: boolean;
  isLoading: boolean;
  appendMessageToCache: (msgs: Message[], overrideId?: string) => void;
  updateMessageInCache: (messageId: string, updater: Partial<Message> | ((msg: Message) => Message), overrideId?: string) => void;
  fetchNextPage: () => void;
  hasNextPage: boolean;
};

// ============================================================
// COMPONENTES UI
// ============================================================
export interface ChatContainerProps {
  guest?: boolean;
  onUnauthorized?: () => void;
  renderLogo?: ReactNode;
}

export declare const ChatContainer: FC<ChatContainerProps>;

export interface SidebarProps {
  onNavigate?: (path: string) => void;
  currentPath?: string;
  settingsPath?: string;
  dashboardPath?: string;
  homePath?: string;
}

export declare const Sidebar: FC<SidebarProps>;

export interface ConfigDrawerProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export declare const ConfigDrawer: FC<ConfigDrawerProps>;
export declare const ConfigPage: FC;
export declare const SearchBar: FC<any>;
export declare const AnimatedJarvis: FC;