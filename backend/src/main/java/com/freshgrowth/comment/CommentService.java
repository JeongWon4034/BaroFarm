package com.freshgrowth.comment;

import com.freshgrowth.comment.dto.CommentRequest;
import com.freshgrowth.common.AppException;
import com.freshgrowth.post.PostMapper;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class CommentService {
    private final CommentMapper commentMapper;
    private final PostMapper postMapper;

    public CommentService(CommentMapper commentMapper, PostMapper postMapper) {
        this.commentMapper = commentMapper;
        this.postMapper = postMapper;
    }

    public List<Comment> findByPost(Long postId) {
        return commentMapper.findByPostId(postId);
    }

    @Transactional
    public Comment create(Long authorId, Long postId, CommentRequest request) {
        if (postMapper.findById(postId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "POST_NOT_FOUND", "게시글을 찾을 수 없습니다.");
        }
        Comment comment = new Comment();
        comment.setPostId(postId);
        comment.setAuthorId(authorId);
        comment.setContent(request.getContent());
        commentMapper.insert(comment);
        return commentMapper.findById(comment.getCommentId());
    }

    @Transactional
    public Comment update(Long authorId, Long commentId, CommentRequest request) {
        if (commentMapper.findById(commentId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "COMMENT_NOT_FOUND", "댓글을 찾을 수 없습니다.");
        }
        if (commentMapper.update(commentId, authorId, request.getContent()) == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "수정 권한이 없습니다.");
        }
        return commentMapper.findById(commentId);
    }

    @Transactional
    public void delete(Long authorId, Long commentId) {
        if (commentMapper.findById(commentId) == null) {
            throw new AppException(HttpStatus.NOT_FOUND, "COMMENT_NOT_FOUND", "댓글을 찾을 수 없습니다.");
        }
        if (commentMapper.delete(commentId, authorId) == 0) {
            throw new AppException(HttpStatus.FORBIDDEN, "FORBIDDEN", "삭제 권한이 없습니다.");
        }
    }
}
